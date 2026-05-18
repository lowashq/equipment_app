from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    message: str
    sent_at: datetime
    reservation_id: UUID

    model_config = ConfigDict(from_attributes=True)
