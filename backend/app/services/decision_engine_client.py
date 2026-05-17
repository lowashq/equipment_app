import logging
from datetime import date

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Equipment, Reservation, User


logger = logging.getLogger(__name__)


async def check_reservation_allowed(
    user: User,
    equipment: Equipment,
    start_date: date,
    end_date: date,
    db: AsyncSession,
) -> dict:
    active_count = await db.scalar(
        select(func.count())
        .select_from(Reservation)
        .where(
            Reservation.user_id == user.id,
            Reservation.status == "active",
        )
    )
    overdue_count = await db.scalar(
        select(func.count())
        .select_from(Reservation)
        .where(
            Reservation.user_id == user.id,
            Reservation.status == "active",
            Reservation.end_date < date.today(),
        )
    )

    payload = {
        "user_id": str(user.id),
        "equipment_id": str(equipment.id),
        "start_date": str(start_date),
        "end_date": str(end_date),
        "user_role": user.role,
        "user_active_rentals": active_count or 0,
        "user_overdue_rentals": overdue_count or 0,
        "equipment_status": equipment.status,
        "equipment_max_rental_days": equipment.max_rental_days,
        "equipment_type": equipment.type,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{settings.decision_engine_url.rstrip('/')}/decide",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Decision engine unavailable; allowing reservation", exc_info=exc)
        return {
            "approved": True,
            "score": 100,
            "reasons": ["Decision engine unavailable; fail-open"],
        }

    if "approved" not in result:
        logger.warning("Decision engine returned an invalid response; allowing reservation")
        return {
            "approved": True,
            "score": 100,
            "reasons": ["Decision engine returned an invalid response; fail-open"],
        }

    return {
        "approved": bool(result.get("approved")),
        "score": int(result.get("score", 0)),
        "reasons": result.get("reasons") or [],
    }
