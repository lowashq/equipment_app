from urllib.parse import urlencode

import httpx
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User


LOCAL_ROLES = ("admin", "equipment_manager", "staff", "student")


def _realm_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/realms/{settings.keycloak_realm}"


def get_keycloak_login_url() -> str:
    params = {
        "client_id": settings.keycloak_client_id,
        "redirect_uri": settings.keycloak_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
    }
    return f"{_realm_url(settings.keycloak_public_url)}/protocol/openid-connect/auth?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    token_url = f"{_realm_url(settings.keycloak_url)}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.keycloak_client_id,
        "code": code,
        "redirect_uri": settings.keycloak_redirect_uri,
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


def _role_from_user_info(user_info: dict) -> str:
    token_roles = user_info.get("realm_access", {}).get("roles", [])

    for role in LOCAL_ROLES:
        if role in token_roles:
            return role

    email = user_info.get("email", "").lower()
    if email.endswith("@student.san.edu.pl"):
        return "student"
    if email.endswith("@san.edu.pl"):
        return "staff"

    return "student"


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
    role = _role_from_user_info(user_info)

    result = await db.execute(select(User).where(User.keycloak_id == keycloak_id))
    user = result.scalar_one_or_none()

    if user is None:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

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
