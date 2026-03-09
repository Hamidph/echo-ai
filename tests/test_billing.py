"""
Tests for billing endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_get_pricing_tiers(client: TestClient) -> None:
    """Test that pricing tiers endpoint returns available plans."""
    response = client.get("/api/v1/billing/pricing")

    assert response.status_code == 200
    data = response.json()
    # Should return a list or dict of pricing tiers
    assert data is not None


@pytest.mark.asyncio
async def test_get_usage(client: TestClient, auth_headers: dict) -> None:
    """Test that usage endpoint returns current quota info."""
    response = client.get("/api/v1/billing/usage", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "prompts_used" in data or "used" in data or "monthly_quota" in data


@pytest.mark.asyncio
async def test_get_usage_requires_auth(client: TestClient) -> None:
    """Test that usage endpoint requires authentication."""
    response = client.get("/api/v1/billing/usage")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_checkout_session_requires_auth(client: TestClient) -> None:
    """Test that checkout session creation requires authentication."""
    response = client.post("/api/v1/billing/checkout", json={"tier": "pro"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(client: TestClient) -> None:
    """Test that Stripe webhook rejects invalid signatures."""
    response = client.post(
        "/api/v1/billing/webhook",
        content=b'{"type": "customer.subscription.updated"}',
        headers={"stripe-signature": "invalid_signature"},
    )

    # Should reject with 400 (invalid signature)
    assert response.status_code in (400, 403, 422)
