from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


EquipmentStatus = Literal["available", "reserved", "borrowed", "serviced", "damaged"]


class EquipmentCreate(BaseModel):
    name: str = Field(..., max_length=255)
    type: str = Field(..., max_length=100)
    serial_number: str = Field(..., max_length=255)
    technical_spec: str | None = None
    location: str | None = Field(default=None, max_length=255)
    max_rental_days: int = Field(default=7, ge=1)
    image_url: str | None = Field(default=None, max_length=500)


class EquipmentUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    type: str | None = Field(default=None, max_length=100)
    serial_number: str | None = Field(default=None, max_length=255)
    technical_spec: str | None = None
    location: str | None = Field(default=None, max_length=255)
    status: EquipmentStatus | None = None
    max_rental_days: int | None = Field(default=None, ge=1)
    image_url: str | None = Field(default=None, max_length=500)


class EquipmentResponse(BaseModel):
    id: UUID
    name: str
    type: str
    serial_number: str
    technical_spec: str | None
    location: str | None
    status: EquipmentStatus
    max_rental_days: int
    image_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentStatusUpdate(BaseModel):
    status: EquipmentStatus


class EquipmentHistoryUser(BaseModel):
    full_name: str
    email: str
    role: str


class EquipmentHistoryReturn(BaseModel):
    returned_at: datetime
    condition: str
    notes: str | None


class EquipmentHistoryReservation(BaseModel):
    id: UUID
    start_date: date
    end_date: date
    status: str
    user: EquipmentHistoryUser
    return_info: EquipmentHistoryReturn | None = None
