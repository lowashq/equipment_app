from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.return_schema import ReturnCreate, ReturnDetailResponse, ReturnResponse
from app.services.return_service import get_all_returns, register_return


router = APIRouter()


@router.post("", response_model=ReturnResponse, status_code=status.HTTP_201_CREATED)
async def register_return_endpoint(
    payload: ReturnCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReturnResponse:
    return await register_return(payload.reservation_id, payload, current_user, db)


@router.get("", response_model=list[ReturnDetailResponse])
async def list_returns(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> list[ReturnDetailResponse]:
    return await get_all_returns(db)
