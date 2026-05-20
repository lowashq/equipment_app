import logging
import smtplib
from email.message import EmailMessage
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import Notification, Reservation


logger = logging.getLogger("uvicorn.error")


def _smtp_is_configured() -> bool:
    return bool(
        settings.smtp_host
        and settings.smtp_port
        and settings.smtp_user
        and settings.smtp_password
        and not settings.smtp_user.startswith("your")
        and not settings.smtp_password.startswith("your")
    )


def _twilio_is_configured() -> bool:
    return bool(
        settings.twilio_account_sid
        and settings.twilio_auth_token
        and settings.twilio_phone_number
    )


async def send_email(to: str, subject: str, body: str) -> None:
    if not _smtp_is_configured():
        print(
            "\n".join(
                [
                    "--- Mock email notification ---",
                    f"To: {to}",
                    f"Subject: {subject}",
                    "",
                    body,
                    "--- End mock email notification ---",
                ]
            ),
            flush=True,
        )
        logger.warning(
            "Mock email notification to=%s subject=%s\n%s",
            to,
            subject,
            body,
        )
        return

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    def _send() -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)

    import asyncio

    await asyncio.to_thread(_send)


async def send_sms(to_phone: str, body: str) -> None:
    if not _twilio_is_configured():
        print(f"Mock SMS notification to={to_phone} body={body}", flush=True)
        logger.warning("Mock SMS notification to=%s body=%s", to_phone, body)
        return

    url = (
        "https://api.twilio.com/2010-04-01/Accounts/"
        f"{settings.twilio_account_sid}/Messages.json"
    )
    payload = {
        "From": settings.twilio_phone_number,
        "To": to_phone,
        "Body": body,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            data=payload,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        )
        response.raise_for_status()


async def log_notification(
    user_id: UUID,
    reservation_id: UUID,
    type: str,
    message: str,
    db: AsyncSession,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        reservation_id=reservation_id,
        type=type,
        message=message,
    )
    db.add(notification)
    await db.flush()
    return notification


async def _get_reservation_details(
    reservation: Reservation,
    db: AsyncSession,
) -> Reservation:
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation.id)
        .options(
            selectinload(Reservation.user),
            selectinload(Reservation.equipment),
        )
    )
    detailed_reservation = result.scalar_one_or_none()
    if detailed_reservation is None:
        raise ValueError("Reservation not found")
    return detailed_reservation


def _equipment_location(reservation: Reservation) -> str:
    return reservation.equipment.location or "Not specified"


async def send_reservation_confirmation(
    reservation: Reservation,
    db: AsyncSession,
) -> None:
    reservation = await _get_reservation_details(reservation, db)
    equipment = reservation.equipment
    user = reservation.user

    subject = f"Reservation Confirmed - {equipment.name}"
    body = f"""Hello {user.full_name},

Your reservation has been confirmed.

Equipment: {equipment.name} ({equipment.type})
Serial number: {equipment.serial_number}
Location: {_equipment_location(reservation)}
Reservation period: {reservation.start_date} - {reservation.end_date}

Please pick up the equipment at the specified location on your start date.

University Equipment Rental System
"""

    await send_email(to=user.email, subject=subject, body=body)
    await log_notification(
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        type="email",
        message=body,
        db=db,
    )


async def send_return_reminder(reservation: Reservation, db: AsyncSession) -> None:
    reservation = await _get_reservation_details(reservation, db)
    equipment = reservation.equipment
    user = reservation.user
    message = f"""Hello {user.full_name},

This is a reminder that your rental is due soon.

Equipment: {equipment.name} ({equipment.type})
Return deadline: {reservation.end_date}

Please return the equipment on time to avoid penalties.

University Equipment Rental System
"""

    await send_email(
        to=user.email,
        subject=f"Reminder: Return Due in 2 Days - {equipment.name}",
        body=message,
    )
    await log_notification(
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        type="email",
        message=message,
        db=db,
    )

    phone_number = getattr(reservation.user, "phone_number", None)
    if phone_number:
        await send_sms(phone_number, message)
        await log_notification(
            user_id=reservation.user_id,
            reservation_id=reservation.id,
            type="sms",
            message=message,
            db=db,
        )


async def send_cancellation_email(
    reservation: Reservation,
    db: AsyncSession,
) -> None:
    reservation = await _get_reservation_details(reservation, db)
    equipment = reservation.equipment
    user = reservation.user

    subject = f"Reservation Cancelled - {equipment.name}"
    body = f"""Hello {user.full_name},

Your reservation has been cancelled.

Equipment: {equipment.name} ({equipment.type})
Original period: {reservation.start_date} - {reservation.end_date}

If this was a mistake, you can make a new reservation at any time.

University Equipment Rental System
"""

    await send_email(to=user.email, subject=subject, body=body)
    await log_notification(
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        type="email",
        message=body,
        db=db,
    )


async def send_overdue_notice(
    reservation: Reservation,
    db: AsyncSession,
) -> None:
    reservation = await _get_reservation_details(reservation, db)
    equipment = reservation.equipment
    user = reservation.user

    subject = f"Overdue Rental - {equipment.name}"
    body = f"""Hello {user.full_name},

Your rental is overdue.

Equipment: {equipment.name} ({equipment.type})
Serial number: {equipment.serial_number}
Original return deadline: {reservation.end_date}

Please return the equipment as soon as possible or contact staff if you need help.

University Equipment Rental System
"""

    await send_email(to=user.email, subject=subject, body=body)
    await log_notification(
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        type="email",
        message=body,
        db=db,
    )


async def get_user_notifications(user_id: UUID, db: AsyncSession) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.sent_at.desc())
    )
    return list(result.scalars().all())
