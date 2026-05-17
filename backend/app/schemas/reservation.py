from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.equipment import EquipmentResponse
from app.schemas.user import UserResponse


ReservationStatus = Literal["pending", "active", "completed", "cancelled"]


class ReservationCreate(BaseModel):
    equipment_id: UUID
    start_date: date
    end_date: date


class ReservationResponse(BaseModel):
    id: UUID
    user_id: UUID
    equipment_id: UUID
    start_date: date
    end_date: date
    status: ReservationStatus
    created_at: datetime
    user: UserResponse
    equipment: EquipmentResponse

    model_config = ConfigDict(from_attributes=True)
