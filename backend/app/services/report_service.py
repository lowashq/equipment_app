import csv
from datetime import datetime, timezone
from io import BytesIO, StringIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Equipment, FaultReport, Reservation


REPORT_COLUMNS = [
    "reservation_id",
    "user_email",
    "user_name",
    "equipment_name",
    "equipment_type",
    "serial_number",
    "start_date",
    "end_date",
    "status",
    "return_condition",
    "return_notes",
]

EQUIPMENT_STATUSES = ["available", "reserved", "borrowed", "damaged"]


async def _count(db: AsyncSession, stmt) -> int:
    result = await db.execute(stmt)
    return int(result.scalar_one() or 0)


async def get_rental_statistics(db: AsyncSession) -> dict[str, Any]:
    total_equipment = await _count(db, select(func.count(Equipment.id)))
    total_reservations = await _count(db, select(func.count(Reservation.id)))
    active_reservations = await _count(
        db,
        select(func.count(Reservation.id)).where(Reservation.status == "active"),
    )
    completed_reservations = await _count(
        db,
        select(func.count(Reservation.id)).where(Reservation.status == "completed"),
    )
    cancelled_reservations = await _count(
        db,
        select(func.count(Reservation.id)).where(Reservation.status == "cancelled"),
    )

    status_result = await db.execute(
        select(Equipment.status, func.count(Equipment.id)).group_by(Equipment.status)
    )
    equipment_by_status = {status: 0 for status in EQUIPMENT_STATUSES}
    for status, count in status_result.all():
        if status in equipment_by_status:
            equipment_by_status[status] = int(count)

    rented_result = await db.execute(
        select(
            Equipment.name,
            Equipment.type,
            func.count(Reservation.id).label("rental_count"),
        )
        .join(Reservation, Reservation.equipment_id == Equipment.id)
        .group_by(Equipment.id, Equipment.name, Equipment.type)
        .order_by(func.count(Reservation.id).desc(), Equipment.name.asc())
        .limit(5)
    )
    most_rented_equipment = [
        {
            "name": name,
            "type": equipment_type,
            "rental_count": int(rental_count),
        }
        for name, equipment_type, rental_count in rented_result.all()
    ]

    fault_reports_unresolved = await _count(
        db,
        select(func.count(FaultReport.id)).where(FaultReport.resolved_at.is_(None)),
    )

    return {
        "total_equipment": total_equipment,
        "total_reservations": total_reservations,
        "active_reservations": active_reservations,
        "completed_reservations": completed_reservations,
        "cancelled_reservations": cancelled_reservations,
        "equipment_by_status": equipment_by_status,
        "most_rented_equipment": most_rented_equipment,
        "fault_reports_unresolved": fault_reports_unresolved,
    }


async def _get_reservations_for_export(db: AsyncSession) -> list[Reservation]:
    result = await db.execute(
        select(Reservation)
        .options(
            selectinload(Reservation.user),
            selectinload(Reservation.equipment),
            selectinload(Reservation.return_record),
        )
        .order_by(Reservation.created_at.desc())
    )
    return list(result.scalars().all())


def _reservation_row(reservation: Reservation) -> list[str]:
    return_record = reservation.return_record
    return [
        str(reservation.id),
        reservation.user.email,
        reservation.user.full_name,
        reservation.equipment.name,
        reservation.equipment.type,
        reservation.equipment.serial_number,
        reservation.start_date.isoformat(),
        reservation.end_date.isoformat(),
        reservation.status,
        return_record.condition if return_record else "",
        return_record.notes if return_record and return_record.notes else "",
    ]


async def export_reservations_csv(db: AsyncSession) -> str:
    reservations = await _get_reservations_for_export(db)
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(REPORT_COLUMNS)

    for reservation in reservations:
        writer.writerow(_reservation_row(reservation))

    return buffer.getvalue()


def _shorten(value: str, max_length: int = 32) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3]}..."


async def export_reservations_pdf(db: AsyncSession) -> bytes:
    statistics = await get_rental_statistics(db)
    reservations = await _get_reservations_for_export(db)

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(
            "University Equipment Rental System - Rental Report",
            styles["Title"],
        ),
        Paragraph(
            f"Generated date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Normal"],
        ),
        Spacer(1, 12),
        Paragraph("Summary statistics", styles["Heading2"]),
    ]

    summary_data = [
        ["Metric", "Value"],
        ["Total equipment", statistics["total_equipment"]],
        ["Total reservations", statistics["total_reservations"]],
        ["Active reservations", statistics["active_reservations"]],
        ["Completed reservations", statistics["completed_reservations"]],
        ["Cancelled reservations", statistics["cancelled_reservations"]],
        ["Unresolved fault reports", statistics["fault_reports_unresolved"]],
    ]
    summary_table = Table(summary_data, hAlign="LEFT")
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.extend([summary_table, Spacer(1, 14), Paragraph("Reservations", styles["Heading2"])])

    table_data = [
        [
            "ID",
            "User",
            "Equipment",
            "Type",
            "Serial",
            "Start",
            "End",
            "Status",
            "Condition",
            "Notes",
        ]
    ]
    for reservation in reservations:
        row = _reservation_row(reservation)
        table_data.append(
            [
                _shorten(row[0], 10),
                _shorten(row[1], 24),
                _shorten(row[3], 22),
                _shorten(row[4], 14),
                _shorten(row[5], 18),
                row[6],
                row[7],
                row[8],
                row[9],
                _shorten(row[10], 28),
            ]
        )

    reservation_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[48, 120, 110, 60, 88, 58, 58, 58, 58, 120],
    )
    reservation_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(reservation_table)

    document.build(elements)
    return buffer.getvalue()
