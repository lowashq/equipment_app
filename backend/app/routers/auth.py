from fastapi import APIRouter, Depends, HTTPException, status
from httpx import HTTPStatusError
from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, get_current_user
from app.auth.keycloak import (
    exchange_code_for_token,
    get_claims_from_access_token,
    get_keycloak_login_url,
    get_keycloak_logout_url,
    get_keycloak_registration_url,
    get_keycloak_user_info,
    sync_keycloak_user,
)
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    AuthUserResponse,
    KeycloakLoginResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UNIVERSITY_EMAIL_MESSAGE = (
    "Registration is only allowed for university members. "
    "Use your @student.san.edu.pl or @san.edu.pl email address."
)


def _role_from_email(email: str) -> str:
    email = email.lower()

    if email.endswith("@student.san.edu.pl"):
        return "student"
    if email.endswith("@san.edu.pl"):
        return "staff"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=UNIVERSITY_EMAIL_MESSAGE,
    )


def _create_token_response(user: User) -> TokenResponse:
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )
    return TokenResponse(access_token=access_token, user=AuthUserResponse.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    email = payload.email.lower()
    role = _role_from_email(email)

    result = await db.execute(select(User).where(func.lower(User.email) == email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    user = User(
        email=email,
        full_name=payload.full_name,
        hashed_password=pwd_context.hash(payload.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return _create_token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    email = payload.email.lower()
    result = await db.execute(select(User).where(func.lower(User.email) == email))
    user = result.scalar_one_or_none()

    if (
        user is None
        or user.hashed_password is None
        or not pwd_context.verify(payload.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _create_token_response(user)


@router.get("/keycloak/login", response_model=KeycloakLoginResponse)
async def keycloak_login() -> KeycloakLoginResponse:
    return KeycloakLoginResponse(url=get_keycloak_login_url())


@router.get("/keycloak/register", response_model=KeycloakLoginResponse)
async def keycloak_register() -> KeycloakLoginResponse:
    return KeycloakLoginResponse(url=get_keycloak_registration_url())


@router.get("/keycloak/logout", response_model=KeycloakLoginResponse)
async def keycloak_logout() -> KeycloakLoginResponse:
    return KeycloakLoginResponse(url=get_keycloak_logout_url())


@router.get("/keycloak/callback", response_model=TokenResponse)
async def keycloak_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        token_data = await exchange_code_for_token(code)
        user_info = await get_keycloak_user_info(token_data["access_token"])
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate with Keycloak",
        ) from exc

    claims = get_claims_from_access_token(token_data["access_token"])
    user_info["realm_access"] = claims.get("realm_access", {})
    user = await sync_keycloak_user(user_info, db)

    return _create_token_response(user)


@router.get("/me", response_model=AuthUserResponse)
async def me(user: User = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse.model_validate(user)
