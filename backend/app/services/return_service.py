from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Reservation, Return, User
from app.schemas.return_schema import ReturnCreate


async def register_return(
    reservation_id,
    data: ReturnCreate,
    current_user: User,
    db: AsyncSession,
) -> Return:
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .options(
            selectinload(Reservation.equipment),
            selectinload(Reservation.return_record),
        )
    )
    reservation = result.scalar_one_or_none()

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found",
        )

    if reservation.status not in {"active", "pending"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active or pending reservations can be returned",
        )

    if reservation.return_record is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return has already been registered for this reservation",
        )

    return_record = Return(
        reservation_id=reservation.id,
        condition=data.condition,
        notes=data.notes,
        reported_by=current_user.id,
    )
    reservation.status = "completed"
    reservation.equipment.status = "damaged" if data.condition == "damaged" else "available"

    db.add(return_record)
    await db.commit()
    await db.refresh(return_record)
    return return_record


async def get_all_returns(db: AsyncSession) -> list[Return]:
    result = await db.execute(
        select(Return)
        .options(
            selectinload(Return.reservation).selectinload(Reservation.user),
            selectinload(Return.reservation).selectinload(Reservation.equipment),
        )
        .order_by(Return.returned_at.desc())
    )
    return list(result.scalars().all())
