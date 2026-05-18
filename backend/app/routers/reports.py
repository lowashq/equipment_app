from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import require_role
from app.database import get_db
from app.models import User
from app.services.report_service import (
    export_reservations_csv,
    export_reservations_pdf,
    get_rental_statistics,
)


router = APIRouter()


@router.get("/statistics")
async def rental_statistics(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> dict[str, Any]:
    return await get_rental_statistics(db)


@router.get(
    "/export/csv",
    response_class=Response,
    responses={
        200: {
            "content": {
                "text/csv": {
                    "schema": {"type": "string", "format": "binary"},
                }
            },
            "description": "CSV file download",
        }
    },
)
async def export_csv(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> Response:
    csv_string = await export_reservations_csv(db)
    return Response(
        content=csv_string,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rentals.csv"},
    )


@router.get(
    "/export/pdf",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/pdf": {
                    "schema": {"type": "string", "format": "binary"},
                }
            },
            "description": "PDF file download",
        }
    },
)
async def export_pdf(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("equipment_manager", "admin")),
) -> Response:
    pdf_bytes = await export_reservations_pdf(db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rentals.pdf"},
    )
