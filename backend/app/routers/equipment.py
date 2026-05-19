from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentHistoryReservation,
    EquipmentResponse,
    EquipmentStatus,
    EquipmentStatusUpdate,
    EquipmentUpdate,
)
from app.services.equipment_service import (
    create_equipment,
    delete_equipment,
    get_all_equipment,
    get_equipment_by_id,
    get_equipment_history,
    update_equipment,
    update_equipment_status,
)


router = APIRouter()


@router.get("", response_model=list[EquipmentResponse])
async def list_equipment(
    equipment_type: Annotated[str | None, Query(alias="type")] = None,
    equipment_status: Annotated[EquipmentStatus | None, Query(alias="status")] = None,
    location: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[EquipmentResponse]:
    filters = {
        "type": equipment_type,
        "status": equipment_status,
        "location": location,
        "search": search,
    }
    return await get_all_equipment(filters, db)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def read_equipment(
    equipment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    return await get_equipment_by_id(equipment_id, db)


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment_endpoint(
    payload: EquipmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> EquipmentResponse:
    return await create_equipment(payload, db)


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment_endpoint(
    equipment_id: UUID,
    payload: EquipmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> EquipmentResponse:
    return await update_equipment(equipment_id, payload, db)


@router.delete("/{equipment_id}")
async def delete_equipment_endpoint(
    equipment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> dict[str, str]:
    await delete_equipment(equipment_id, db)
    return {"message": "Equipment deleted successfully"}


@router.get("/{equipment_id}/history", response_model=list[EquipmentHistoryReservation])
async def read_equipment_history(
    equipment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[EquipmentHistoryReservation]:
    return await get_equipment_history(equipment_id, db)


@router.patch("/{equipment_id}/status", response_model=EquipmentResponse)
async def patch_equipment_status(
    equipment_id: UUID,
    payload: EquipmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> EquipmentResponse:
    return await update_equipment_status(equipment_id, payload.status, db)
