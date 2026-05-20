from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Equipment, FaultReport, Notification, Reservation, Return
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


VALID_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "available": {"reserved", "damaged"},
    "reserved": {"borrowed", "available", "damaged"},
    "borrowed": {"available", "damaged"},
    "damaged": {"available"},
}


def validate_status_transition(current_status: str, new_status: str) -> None:
    if current_status == new_status:
        return

    allowed_statuses = VALID_STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}",
        )


async def resolve_fault_reports_for_available_equipment(
    equipment_id: UUID,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(FaultReport).where(
            FaultReport.equipment_id == equipment_id,
            FaultReport.resolved_at.is_(None),
        )
    )
    resolved_at = datetime.now(timezone.utc)

    for report in result.scalars().all():
        report.resolved_at = resolved_at


async def get_all_equipment(filters: dict[str, str | None], db: AsyncSession) -> list[Equipment]:
    stmt = select(Equipment).order_by(Equipment.created_at.desc())

    if filters.get("type"):
        stmt = stmt.where(Equipment.type == filters["type"])

    if filters.get("status"):
        stmt = stmt.where(Equipment.status == filters["status"])

    if filters.get("location"):
        stmt = stmt.where(Equipment.location.ilike(f"%{filters['location']}%"))

    if filters.get("search"):
        search_term = f"%{filters['search']}%"
        stmt = stmt.where(
            or_(
                Equipment.name.ilike(search_term),
                Equipment.type.ilike(search_term),
                Equipment.serial_number.ilike(search_term),
                Equipment.technical_spec.ilike(search_term),
            )
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_equipment_by_id(equipment_id: UUID, db: AsyncSession) -> Equipment:
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()

    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    return equipment


async def create_equipment(data: EquipmentCreate, db: AsyncSession) -> Equipment:
    equipment = Equipment(**data.model_dump())
    db.add(equipment)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment with this serial number already exists",
        ) from exc

    await db.refresh(equipment)
    return equipment


async def update_equipment(equipment_id: UUID, data: EquipmentUpdate, db: AsyncSession) -> Equipment:
    equipment = await get_equipment_by_id(equipment_id, db)
    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] is not None:
        validate_status_transition(equipment.status, update_data["status"])

    for field, value in update_data.items():
        setattr(equipment, field, value)

    if update_data.get("status") == "available":
        await resolve_fault_reports_for_available_equipment(equipment.id, db)

    equipment.updated_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment with this serial number already exists",
        ) from exc

    await db.refresh(equipment)
    return equipment


async def update_equipment_status(
    equipment_id: UUID,
    new_status: str,
    db: AsyncSession,
) -> Equipment:
    equipment = await get_equipment_by_id(equipment_id, db)
    validate_status_transition(equipment.status, new_status)

    equipment.status = new_status
    if new_status == "available":
        await resolve_fault_reports_for_available_equipment(equipment.id, db)

    equipment.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(equipment)
    return equipment


async def delete_equipment(equipment_id: UUID, db: AsyncSession) -> None:
    equipment = await get_equipment_by_id(equipment_id, db)

    try:
        reservation_ids_result = await db.execute(
            select(Reservation.id).where(Reservation.equipment_id == equipment_id)
        )
        reservation_ids = list(reservation_ids_result.scalars().all())

        if reservation_ids:
            await db.execute(
                delete(Notification).where(Notification.reservation_id.in_(reservation_ids))
            )
            await db.execute(delete(Return).where(Return.reservation_id.in_(reservation_ids)))
            await db.execute(delete(Reservation).where(Reservation.id.in_(reservation_ids)))

        await db.execute(delete(FaultReport).where(FaultReport.equipment_id == equipment_id))
        await db.delete(equipment)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment cannot be deleted because it has related records",
        ) from exc


async def get_equipment_history(equipment_id: UUID, db: AsyncSession) -> list[dict[str, Any]]:
    await get_equipment_by_id(equipment_id, db)

    result = await db.execute(
        select(Reservation)
        .where(Reservation.equipment_id == equipment_id)
        .options(
            selectinload(Reservation.user),
            selectinload(Reservation.return_record),
        )
        .order_by(Reservation.created_at.desc())
    )
    reservations = result.scalars().all()

    history = []
    for reservation in reservations:
        return_record = reservation.return_record
        history.append(
            {
                "id": reservation.id,
                "start_date": reservation.start_date,
                "end_date": reservation.end_date,
                "status": reservation.status,
                "user": {
                    "full_name": reservation.user.full_name,
                    "email": reservation.user.email,
                    "role": reservation.user.role,
                },
                "return_info": None
                if return_record is None
                else {
                    "returned_at": return_record.returned_at,
                    "condition": return_record.condition,
                    "notes": return_record.notes,
                },
            }
        )

    return history
