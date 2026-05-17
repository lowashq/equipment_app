from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationStatus
from app.services.reservation_service import (
    ReservationRejectedError,
    cancel_reservation,
    create_reservation,
    get_user_reservations,
)


router = APIRouter()


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
        return await create_reservation(current_user, payload, db)
    except ReservationRejectedError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Reservation rejected by decision engine",
                "reasons": exc.reasons,
                "score": exc.score,
            },
        )


@router.delete("/{reservation_id}")
async def cancel_reservation_endpoint(
    reservation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    return await cancel_reservation(reservation_id, current_user, db)
