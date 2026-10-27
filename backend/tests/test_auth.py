from datetime import timedelta

import jwt
import pytest
from httpx import AsyncClient

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.enums import UserRole


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
