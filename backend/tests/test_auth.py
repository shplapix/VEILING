from datetime import timedelta

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User


def test_password_hashing() -> None:
    raw_pass = "ArchiveMasterPiece2026!"
    hashed = get_password_hash(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_and_decode_access_token() -> None:
    data = {"sub": "123e4567-e89b-12d3-a456-426614174000", "role": "ADMIN"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=15))
    payload = decode_access_token(token)
    assert payload["sub"] == "123e4567-e89b-12d3-a456-426614174000"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload


def test_expired_token_raises_error() -> None:
    data = {"sub": "expired-user"}
    token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(token)


def test_token_missing_required_claims_raises_error() -> None:
    raw_token_no_exp = jwt.encode(
        {"sub": "test-user"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(raw_token_no_exp)

    raw_token_no_sub = jwt.encode(
        {"exp": 9999999999},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(raw_token_no_sub)


async def test_auth_register_and_login_flow(client: AsyncClient) -> None:
    register_payload = {
        "email": "archivist@antwerp.be",
        "password": "SecurePassword123!",
        "full_name": "Antwerp Archivist",
        "role": "SELLER",
    }
    reg_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "archivist@antwerp.be"
    assert reg_data["user"]["role"] == "SELLER"

    dup_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert dup_response.status_code == 409

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "archivist@antwerp.be", "password": "SecurePassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "archivist@antwerp.be", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    not_found_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@antwerp.be", "password": "AnyPassword123!"},
    )
    assert not_found_login.status_code == 401

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "archivist@antwerp.be"

    unauth_me = await client.get("/api/v1/auth/me")
    assert unauth_me.status_code == 401

    invalid_me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert invalid_me.status_code == 401


async def test_admin_registration_forbidden(client: AsyncClient) -> None:
    admin_payload = {
        "email": "attacker@evil.com",
        "password": "EvilPassword123!",
        "role": "ADMIN",
    }
    response = await client.post("/api/v1/auth/register", json=admin_payload)
    assert response.status_code in (422, 403)


async def test_email_case_insensitivity_in_auth(client: AsyncClient) -> None:
    payload = {
        "email": "CaseCurator@Antwerp.be",
        "password": "ValidPassword123!",
        "role": "SELLER",
    }
    reg = await client.post("/api/v1/auth/register", json=payload)
    assert reg.status_code == 201

    login_lower = await client.post(
        "/api/v1/auth/login",
        json={"email": "casecurator@antwerp.be", "password": "ValidPassword123!"},
    )
    assert login_lower.status_code == 200

    login_upper = await client.post(
        "/api/v1/auth/login",
        json={"email": "CASECURATOR@ANTWERP.BE", "password": "ValidPassword123!"},
    )
    assert login_upper.status_code == 200


async def test_inactive_user_auth_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    inactive_user = User(
        email="blocked@veiling.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.SELLER,
        is_active=False,
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "blocked@veiling.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 403
    assert login_resp.json()["detail"] == "Account is inactive"

    valid_token = create_access_token(data={"sub": str(inactive_user.id)})
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {valid_token}"},
    )
    assert me_resp.status_code == 403
    assert me_resp.json()["detail"] == "Inactive user"


async def test_password_length_validation(client: AsyncClient) -> None:
    short_pass = {
        "email": "short@veiling.com",
        "password": "short",
        "role": "SELLER",
    }
    resp_short = await client.post("/api/v1/auth/register", json=short_pass)
    assert resp_short.status_code == 422

    long_pass = {
        "email": "long@veiling.com",
        "password": "A" * 73,
        "role": "SELLER",
    }
    resp_long = await client.post("/api/v1/auth/register", json=long_pass)
    assert resp_long.status_code == 422


async def test_role_dependencies() -> None:
    from fastapi import HTTPException

    from app.api.deps import (
        get_current_active_user,
        get_current_admin,
        get_current_seller,
    )
    from app.models.user import User

    active_customer = User(
        email="cust@veiling.com",
        hashed_password="h",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    inactive_seller = User(
        email="inact@veiling.com",
        hashed_password="h",
        role=UserRole.SELLER,
        is_active=False,
    )
    active_seller = User(
        email="sell@veiling.com",
        hashed_password="h",
        role=UserRole.SELLER,
        is_active=True,
    )
    active_admin = User(
        email="admin@veiling.com",
        hashed_password="h",
        role=UserRole.ADMIN,
        is_active=True,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(inactive_seller)
    assert exc_info.value.status_code == 403

    assert await get_current_active_user(active_seller) == active_seller

    with pytest.raises(HTTPException) as exc_info:
        await get_current_seller(active_customer)
    assert exc_info.value.status_code == 403

    assert await get_current_seller(active_seller) == active_seller
    assert await get_current_seller(active_admin) == active_admin

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(active_seller)
    assert exc_info.value.status_code == 403

    assert await get_current_admin(active_admin) == active_admin
