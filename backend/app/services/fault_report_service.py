from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Equipment, FaultReport, User
from app.schemas.fault_report import FaultReportCreate


async def create_fault_report(
    data: FaultReportCreate,
    current_user: User,
    db: AsyncSession,
) -> FaultReport:
    equipment = await db.scalar(select(Equipment).where(Equipment.id == data.equipment_id))
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    report = FaultReport(
        equipment_id=data.equipment_id,
        user_id=current_user.id,
        description=data.description,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_fault_reports(
    current_user: User,
    db: AsyncSession,
    equipment_id: UUID | None = None,
) -> list[FaultReport]:
    stmt = select(FaultReport).order_by(FaultReport.created_at.desc())

    if current_user.role not in {"admin", "equipment_manager"}:
        stmt = stmt.where(FaultReport.user_id == current_user.id)

    if equipment_id is not None:
        stmt = stmt.where(FaultReport.equipment_id == equipment_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def resolve_fault_report(report_id: UUID, db: AsyncSession) -> FaultReport:
    report = await db.scalar(select(FaultReport).where(FaultReport.id == report_id))
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fault report not found",
        )

    report.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(report)
    return report
