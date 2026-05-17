from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


ReturnCondition = Literal["good", "damaged"]


class ReturnCreate(BaseModel):
    reservation_id: UUID
    condition: ReturnCondition = "good"
    notes: str | None = None


class ReturnResponse(BaseModel):
    id: UUID
    reservation_id: UUID
    returned_at: datetime
    condition: ReturnCondition
    notes: str | None
    reported_by: UUID

    model_config = ConfigDict(from_attributes=True)
