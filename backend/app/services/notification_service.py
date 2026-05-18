import logging
import smtplib
from email.message import EmailMessage
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
            f"Mock email notification to={to} subject={subject} body={body}",
            flush=True,
        )
        logger.warning(
            "Mock email notification to=%s subject=%s body=%s",
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


async def send_return_reminder(reservation: Reservation, db: AsyncSession) -> None:
    message = (
        f"Your rental of {reservation.equipment.name} is due on {reservation.end_date}. "
        "Please return it on time to avoid penalties."
    )

    await send_email(
        to=reservation.user.email,
        subject="Equipment return reminder",
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


async def get_user_notifications(user_id: UUID, db: AsyncSession) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.sent_at.desc())
    )
    return list(result.scalars().all())
