import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Reservation
from app.services.notification_service import send_return_reminder


logger = logging.getLogger("uvicorn.error")


async def check_upcoming_returns(db: AsyncSession | None = None) -> None:
    owns_session = db is None
    session = db or AsyncSessionLocal()

    try:
        target_date = date.today() + timedelta(days=2)
        result = await session.execute(
            select(Reservation)
            .where(
                Reservation.status.in_(("active", "pending")),
                Reservation.end_date == target_date,
            )
            .options(
                selectinload(Reservation.user),
                selectinload(Reservation.equipment),
            )
        )
        reservations = list(result.scalars().all())

        for reservation in reservations:
            await send_return_reminder(reservation, session)

        if reservations:
            await session.commit()

        print(
            f"Upcoming return reminder check completed; reminders={len(reservations)}",
            flush=True,
        )
        logger.warning(
            "Upcoming return reminder check completed; reminders=%s",
            len(reservations),
        )
    except Exception:
        if owns_session:
            await session.rollback()
        logger.exception("Upcoming return reminder check failed")
        raise
    finally:
        if owns_session:
            await session.close()
