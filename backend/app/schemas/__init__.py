from app.schemas.auth import (
    AuthUserResponse,
    KeycloakLoginResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentHistoryReservation,
    EquipmentResponse,
    EquipmentStatusUpdate,
    EquipmentUpdate,
)
from app.schemas.fault_report import FaultReportCreate, FaultReportResponse
from app.schemas.notification import NotificationResponse
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.schemas.return_schema import ReturnCreate, ReturnDetailResponse, ReturnResponse
from app.schemas.user import UserCreate, UserResponse, UserRoleUpdate

__all__ = [
    "EquipmentCreate",
    "EquipmentHistoryReservation",
    "EquipmentResponse",
    "EquipmentStatusUpdate",
    "EquipmentUpdate",
    "FaultReportCreate",
    "FaultReportResponse",
    "NotificationResponse",
    "ReservationCreate",
    "ReservationResponse",
    "ReturnCreate",
    "ReturnDetailResponse",
    "ReturnResponse",
    "AuthUserResponse",
    "KeycloakLoginResponse",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
    "UserRoleUpdate",
]
