"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole, PricingTier


@pytest.mark.asyncio
async def test_register_user(client: TestClient, db_session: AsyncSession) -> None:
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["pricing_tier"] == "free"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: TestClient, db_session: AsyncSession) -> None:
    """Test that registering with duplicate email fails."""
    # Create a user
    user = User(
        email="existing@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=100,
    )
    db_session.add(user)
    await db_session.commit()

    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "password": "newpassword",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: TestClient, db_session: AsyncSession) -> None:
    """Test successful login."""
    # Create a user
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=100,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: TestClient, db_session: AsyncSession) -> None:
    """Test login with wrong password."""
    # Create a user
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=100,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test getting current user info."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_create_api_key(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test creating an API key."""
    response = client.post(
        "/api/v1/auth/api-keys",
        json={"name": "Test API Key"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test API Key"
    assert "key" in data  # Full key returned only once
    assert data["key"].startswith("sk_live_")


@pytest.mark.asyncio
async def test_list_api_keys(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test listing API keys."""
    # Create an API key first
    client.post(
        "/api/v1/auth/api-keys",
        json={"name": "Test Key"},
        headers=auth_headers,
    )

    # List keys
    response = client.get("/api/v1/auth/api-keys", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Full key should not be in list response
    assert "key" not in data[0] or data[0]["key"] is None
