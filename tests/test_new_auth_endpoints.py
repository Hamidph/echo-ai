"""
Tests for the new authentication endpoints:
- POST /auth/forgot-password
- POST /auth/reset-password
- POST /auth/verify-email
- POST /auth/resend-verification
- DELETE /auth/me
"""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import create_access_token, get_password_hash
from backend.app.models.user import PricingTier, User, UserRole


@pytest.mark.asyncio
async def test_forgot_password_known_email(client: TestClient, db_session: AsyncSession) -> None:
    """Test forgot-password with a registered email returns 200."""
    user = User(
        email="forgot@example.com",
        hashed_password=get_password_hash("oldpass"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=3,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "forgot@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(client: TestClient, db_session: AsyncSession) -> None:
    """Test forgot-password with unknown email still returns 200 (anti-enumeration)."""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_reset_password_valid_token(client: TestClient, db_session: AsyncSession) -> None:
    """Test reset-password with a valid token updates the password."""
    user = User(
        email="reset@example.com",
        hashed_password=get_password_hash("oldpass"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=3,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate a valid password reset token
    token = create_access_token(
        data={"user_id": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=1),
    )

    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "newpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify we can now log in with the new password
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "reset@example.com", "password": "newpassword123"},
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: TestClient) -> None:
    """Test reset-password with an invalid token returns 400."""
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-valid-token", "new_password": "newpassword123"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_wrong_token_type(
    client: TestClient, db_session: AsyncSession
) -> None:
    """Test reset-password rejects a verification token (wrong type)."""
    user = User(
        email="wrongtype@example.com",
        hashed_password=get_password_hash("pass"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=3,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate a verification token (wrong type for reset)
    token = create_access_token(
        data={"user_id": str(user.id), "type": "email_verification"},
        expires_delta=timedelta(hours=24),
    )

    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "newpassword123"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_email_valid_token(client: TestClient, db_session: AsyncSession) -> None:
    """Test verify-email with a valid token marks user as verified."""
    user = User(
        email="verify@example.com",
        hashed_password=get_password_hash("pass"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=3,
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_verified is False

    # Generate a valid verification token
    token = create_access_token(
        data={"user_id": str(user.id), "type": "email_verification"},
        expires_delta=timedelta(hours=24),
    )

    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: TestClient) -> None:
    """Test verify-email with an invalid token returns 400."""
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": "garbage-token"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_email_already_verified(client: TestClient, db_session: AsyncSession) -> None:
    """Test verify-email on already verified user returns 200 with 'already verified'."""
    user = User(
        email="alreadyverified@example.com",
        hashed_password=get_password_hash("pass"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=3,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(
        data={"user_id": str(user.id), "type": "email_verification"},
        expires_delta=timedelta(hours=24),
    )

    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )

    assert response.status_code == 200
    assert "already verified" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_delete_account(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test DELETE /auth/me deletes the account."""
    # Verify user can access /me before deletion
    me_response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response.status_code == 200

    # Delete account
    delete_response = client.delete("/api/v1/auth/me", headers=auth_headers)
    assert delete_response.status_code == 204

    # Verify user can no longer authenticate
    me_response_after = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response_after.status_code == 401


@pytest.mark.asyncio
async def test_delete_account_requires_auth(client: TestClient) -> None:
    """Test that DELETE /auth/me requires authentication."""
    response = client.delete("/api/v1/auth/me")
    assert response.status_code == 401
