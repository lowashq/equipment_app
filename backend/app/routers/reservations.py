import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationStatus
from app.services.notification_service import (
    send_cancellation_email,
    send_reservation_confirmation,
)
from app.services.reservation_service import (
    ReservationRejectedError,
    approve_reservation,
    cancel_reservation,
    create_reservation,
    get_user_reservations,
)


router = APIRouter()
logger = logging.getLogger("uvicorn.error")


async def _send_notification_safely(notification_call, db: AsyncSession) -> None:
    try:
        await notification_call()
        await db.commit()
    except Exception:
        logger.exception("Reservation email notification failed")


@router.get("", response_model=list[ReservationResponse])
async def list_reservations(
    reservation_status: Annotated[ReservationStatus | None, Query(alias="status")] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ReservationResponse]:
    return await get_user_reservations(current_user, db, reservation_status)


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation_endpoint(
    payload: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReservationResponse | JSONResponse:
    try:
        reservation = await create_reservation(current_user, payload, db)
    except ReservationRejectedError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Reservation rejected by decision engine",
                "reasons": exc.reasons,
                "score": exc.score,
            },
        )
    await _send_notification_safely(
        lambda: send_reservation_confirmation(reservation, db),
        db,
    )
    return reservation


@router.delete("/{reservation_id}")
async def cancel_reservation_endpoint(
    reservation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    reservation = await cancel_reservation(reservation_id, current_user, db)
    await _send_notification_safely(
        lambda: send_cancellation_email(reservation, db),
        db,
    )
    return {"message": "Reservation cancelled"}


@router.patch("/{reservation_id}/approve", response_model=ReservationResponse)
async def approve_reservation_endpoint(
    reservation_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("staff", "equipment_manager", "admin")),
) -> ReservationResponse:
    return await approve_reservation(reservation_id, db)
