import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Reservation
from app.services.notification_service import send_overdue_notice, send_return_reminder


logger = logging.getLogger("uvicorn.error")


async def check_upcoming_returns(db: AsyncSession | None = None) -> None:
    owns_session = db is None
    session = db or AsyncSessionLocal()

    try:
        target_date = date.today() + timedelta(days=2)
        upcoming_result = await session.execute(
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
        upcoming_reservations = list(upcoming_result.scalars().all())

        overdue_result = await session.execute(
            select(Reservation)
            .where(
                Reservation.status.in_(("active", "pending")),
                Reservation.end_date < date.today(),
            )
            .options(
                selectinload(Reservation.user),
                selectinload(Reservation.equipment),
            )
        )
        overdue_reservations = list(overdue_result.scalars().all())

        for reservation in upcoming_reservations:
            await send_return_reminder(reservation, session)

        for reservation in overdue_reservations:
            await send_overdue_notice(reservation, session)

        if upcoming_reservations or overdue_reservations:
            await session.commit()

        print(
            "Return notification check completed; "
            f"reminders={len(upcoming_reservations)} overdue={len(overdue_reservations)}",
            flush=True,
        )
        logger.warning(
            "Return notification check completed; reminders=%s overdue=%s",
            len(upcoming_reservations),
            len(overdue_reservations),
        )
    except Exception:
        if owns_session:
            await session.rollback()
        logger.exception("Return notification check failed")
        raise
    finally:
        if owns_session:
            await session.close()
