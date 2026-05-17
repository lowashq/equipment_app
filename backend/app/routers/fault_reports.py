from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.fault_report import FaultReportCreate, FaultReportResponse
from app.services.fault_report_service import (
    create_fault_report,
    get_fault_reports,
    resolve_fault_report,
)


router = APIRouter()


@router.post("", response_model=FaultReportResponse, status_code=status.HTTP_201_CREATED)
async def create_fault_report_endpoint(
    payload: FaultReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FaultReportResponse:
    return await create_fault_report(payload, current_user, db)


@router.get("", response_model=list[FaultReportResponse])
async def list_fault_reports(
    equipment_id: Annotated[UUID | None, Query()] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FaultReportResponse]:
    return await get_fault_reports(current_user, db, equipment_id)


@router.patch("/{report_id}/resolve", response_model=FaultReportResponse)
async def resolve_fault_report_endpoint(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> FaultReportResponse:
    return await resolve_fault_report(report_id, db)
