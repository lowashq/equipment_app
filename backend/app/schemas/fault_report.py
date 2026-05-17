from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FaultReportCreate(BaseModel):
    equipment_id: UUID
    description: str


class FaultReportResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    user_id: UUID
    description: str
    created_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
