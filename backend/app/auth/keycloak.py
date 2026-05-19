from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User


LOCAL_ROLES = ("admin", "equipment_manager", "staff", "student")
ELEVATED_ROLES = ("admin", "equipment_manager")


def _realm_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/realms/{settings.keycloak_realm}"


def get_keycloak_login_url() -> str:
    params = {
        "client_id": settings.keycloak_client_id,
        "redirect_uri": settings.keycloak_frontend_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
    }
    return f"{_realm_url(settings.keycloak_public_url)}/protocol/openid-connect/auth?{urlencode(params)}"


def get_keycloak_registration_url() -> str:
    params = {
        "client_id": settings.keycloak_client_id,
        "redirect_uri": settings.keycloak_frontend_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
    }
    return (
        f"{_realm_url(settings.keycloak_public_url)}"
        f"/protocol/openid-connect/registrations?{urlencode(params)}"
    )


def get_keycloak_logout_url() -> str:
    params = {
        "client_id": settings.keycloak_client_id,
        "post_logout_redirect_uri": "http://localhost:3000/login",
    }
    return f"{_realm_url(settings.keycloak_public_url)}/protocol/openid-connect/logout?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    token_url = f"{_realm_url(settings.keycloak_url)}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.keycloak_client_id,
        "code": code,
        "redirect_uri": settings.keycloak_frontend_redirect_uri,
    }

    if settings.keycloak_client_secret:
        data["client_secret"] = settings.keycloak_client_secret

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(token_url, data=data)
        response.raise_for_status()
        return response.json()


async def get_keycloak_user_info(token: str) -> dict:
    user_info_url = f"{_realm_url(settings.keycloak_url)}/protocol/openid-connect/userinfo"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()


def get_claims_from_access_token(token: str) -> dict:
    return jwt.get_unverified_claims(token)


def _role_from_email(email: str) -> str:
    email = email.lower()
    if email.endswith("@student.san.edu.pl"):
        return "student"
    if email.endswith("@san.edu.pl"):
        return "staff"

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Account not allowed. Use your university email.",
    )


def _role_from_user_info(user_info: dict, current_role: str | None = None) -> str:
    baseline_role = _role_from_email(user_info.get("email", ""))
    token_roles = set(user_info.get("realm_access", {}).get("roles", []))

    for role in ELEVATED_ROLES:
        if role in token_roles:
            return role

    if current_role in ELEVATED_ROLES:
        return current_role

    if "staff" in token_roles and baseline_role == "staff":
        return "staff"

    return baseline_role


async def sync_keycloak_user(user_info: dict, db: AsyncSession) -> User:
    keycloak_id = user_info["sub"]
    email = user_info["email"].lower()
    full_name = (
        user_info.get("name")
        or " ".join(
            value
            for value in [user_info.get("given_name"), user_info.get("family_name")]
            if value
        )
        or email
    )

    result = await db.execute(select(User).where(User.keycloak_id == keycloak_id))
    user = result.scalar_one_or_none()

    if user is None:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    role = _role_from_user_info(user_info, user.role if user else None)

    if user is None:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=None,
            role=role,
            keycloak_id=keycloak_id,
            is_active=True,
        )
        db.add(user)
    else:
        user.email = email
        user.full_name = full_name
        user.role = role
        user.keycloak_id = keycloak_id
        user.is_active = True

    await db.commit()
    await db.refresh(user)
    return user
