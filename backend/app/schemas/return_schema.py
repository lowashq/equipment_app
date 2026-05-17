from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.equipment import EquipmentResponse
from app.schemas.user import UserResponse


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


class ReturnReservationResponse(BaseModel):
    id: UUID
    user_id: UUID
    equipment_id: UUID
    start_date: date
    end_date: date
    status: str
    user: UserResponse
    equipment: EquipmentResponse

    model_config = ConfigDict(from_attributes=True)


class ReturnDetailResponse(ReturnResponse):
    reservation: ReturnReservationResponse

    model_config = ConfigDict(from_attributes=True)
