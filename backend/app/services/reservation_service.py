from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Equipment, Reservation, User
from app.schemas.reservation import ReservationCreate
from app.services.decision_engine_client import check_reservation_allowed


class ReservationRejectedError(Exception):
    def __init__(self, reasons: list[str], score: int) -> None:
        self.reasons = reasons
        self.score = score


async def _get_reservation_with_details(
    reservation_id: UUID,
    db: AsyncSession,
) -> Reservation:
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .options(
            selectinload(Reservation.user),
            selectinload(Reservation.equipment),
        )
    )
    reservation = result.scalar_one_or_none()

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found",
        )

    return reservation


async def create_reservation(
    user: User,
    data: ReservationCreate,
    db: AsyncSession,
) -> Reservation:
    if data.end_date < data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation end_date cannot be before start_date",
        )

    result = await db.execute(select(Equipment).where(Equipment.id == data.equipment_id))
    equipment = result.scalar_one_or_none()
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    decision = await check_reservation_allowed(
        user=user,
        equipment=equipment,
        start_date=data.start_date,
        end_date=data.end_date,
        db=db,
    )
    if not decision["approved"]:
        raise ReservationRejectedError(
            reasons=decision["reasons"],
            score=decision["score"],
        )

    reservation_status = "active" if decision["score"] == 100 else "pending"
    equipment_status = "borrowed" if reservation_status == "active" else "reserved"

    reservation = Reservation(
        user_id=user.id,
        equipment_id=equipment.id,
        start_date=data.start_date,
        end_date=data.end_date,
        status=reservation_status,
    )
    equipment.status = equipment_status

    db.add(reservation)
    await db.commit()

    return await _get_reservation_with_details(reservation.id, db)


async def get_user_reservations(
    user: User,
    db: AsyncSession,
    reservation_status: str | None = None,
) -> list[Reservation]:
    stmt = (
        select(Reservation)
        .options(
            selectinload(Reservation.user),
            selectinload(Reservation.equipment),
        )
        .order_by(Reservation.created_at.desc())
    )

    if user.role not in {"admin", "equipment_manager", "staff"}:
        stmt = stmt.where(Reservation.user_id == user.id)

    if reservation_status is not None:
        stmt = stmt.where(Reservation.status == reservation_status)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def cancel_reservation(
    reservation_id: UUID,
    user: User,
    db: AsyncSession,
) -> dict[str, Any]:
    reservation = await _get_reservation_with_details(reservation_id, db)

    if reservation.user_id != user.id and user.role not in {"admin", "equipment_manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to cancel this reservation",
        )

    if reservation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending reservations can be cancelled",
        )

    reservation.status = "cancelled"
    reservation.equipment.status = "available"
    await db.commit()

    return {"message": "Reservation cancelled"}


async def approve_reservation(
    reservation_id: UUID,
    db: AsyncSession,
) -> Reservation:
    reservation = await _get_reservation_with_details(reservation_id, db)

    if reservation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending reservations can be approved",
        )

    if reservation.equipment.status != "reserved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment must be reserved before approving the reservation",
        )

    reservation.status = "active"
    reservation.equipment.status = "borrowed"
    await db.commit()

    return await _get_reservation_with_details(reservation.id, db)
