
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole, PricingTier

@pytest.mark.asyncio
async def test_api_key_auth_flow(client: TestClient, db_session: AsyncSession, auth_headers: dict) -> None:
    """
    Test the full flow of creating and using an API key.
    This verifies that the optimized lookup logic works correctly.
    """
    # 1. Create API Key
    response = client.post(
        "/api/v1/auth/api-keys",
        json={"name": "Integration Test Key"},
        headers=auth_headers,
    )
    if response.status_code != 201:
        print(f"\n[DEBUG] Create API Key failed: {response.status_code} {response.text}")
    assert response.status_code == 201
    api_key = response.json()["key"]
    
    # 2. Use API Key to authenticate
    # We use a different client session or just headers to prove it works without Bearer token
    response = client.get(
        "/api/v1/auth/me",
        headers={"X-API-Key": api_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data
