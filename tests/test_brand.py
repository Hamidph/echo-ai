"""
Tests for brand profile endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User


@pytest.mark.asyncio
async def test_get_brand_profile(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test getting brand profile returns user's brand info."""
    response = client.get("/api/v1/brand/profile", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "brand_name" in data


@pytest.mark.asyncio
async def test_update_brand_profile(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test updating brand profile."""
    response = client.put(
        "/api/v1/brand/profile",
        json={
            "brand_name": "My Startup",
            "brand_description": "We build great things",
            "brand_website": "https://mystartup.com",
            "brand_industry": "Technology",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["brand_name"] == "My Startup"
    assert data["brand_industry"] == "Technology"


@pytest.mark.asyncio
async def test_update_brand_with_webhook_url(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test updating brand profile with webhook URL."""
    response = client.put(
        "/api/v1/brand/profile",
        json={
            "brand_name": "Webhook Test Brand",
            "webhook_url": "https://hooks.example.com/experiments",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["brand_name"] == "Webhook Test Brand"


@pytest.mark.asyncio
async def test_add_competitor(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test adding a competitor to brand profile."""
    response = client.post(
        "/api/v1/brand/competitors",
        json={"competitor_name": "CompetitorA"},
        headers=auth_headers,
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
async def test_remove_competitor(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test removing a competitor from brand profile."""
    # First add a competitor
    client.post(
        "/api/v1/brand/competitors",
        json={"competitor_name": "CompetitorB"},
        headers=auth_headers,
    )

    # Then remove it
    response = client.delete(
        "/api/v1/brand/competitors",
        json={"competitor_name": "CompetitorB"},
        headers=auth_headers,
    )

    assert response.status_code in (200, 204)


@pytest.mark.asyncio
async def test_brand_profile_requires_auth(client: TestClient) -> None:
    """Test brand endpoints require authentication."""
    response = client.get("/api/v1/brand/profile")
    assert response.status_code == 401

    response = client.put("/api/v1/brand/profile", json={"brand_name": "Test"})
    assert response.status_code == 401
