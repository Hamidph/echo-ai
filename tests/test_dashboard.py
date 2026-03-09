"""
Tests for dashboard endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.experiment import BatchRun, BatchRunStatus, Experiment, ExperimentStatus
from backend.app.models.user import User


@pytest.mark.asyncio
async def test_dashboard_stats_empty(
    client: TestClient, auth_headers: dict
) -> None:
    """Test dashboard stats with no experiments returns zeros."""
    with patch("backend.app.routers.dashboard.RedisClient") as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)

        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_experiments"] == 0
    assert data["completed_experiments"] == 0
    assert data["avg_visibility_score"] == 0.0
    assert data["share_of_voice"] == []
    assert data["visibility_trend"] == []


@pytest.mark.asyncio
async def test_dashboard_stats_with_data(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test dashboard stats with completed experiments."""
    exp = Experiment(
        user_id=test_user.id,
        prompt="What is the best CRM?",
        target_brand="TestBrand",
        config={"iterations": 10},
        status=ExperimentStatus.COMPLETED.value,
    )
    db_session.add(exp)
    await db_session.commit()
    await db_session.refresh(exp)

    batch = BatchRun(
        experiment_id=exp.id,
        provider="openai",
        model="gpt-4o",
        status=BatchRunStatus.COMPLETED.value,
        total_iterations=10,
        successful_iterations=8,
        failed_iterations=2,
        total_tokens=1000,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        metrics={
            "target_visibility": {"visibility_rate": 0.75},
            "share_of_voice": [
                {"brand": "TestBrand", "share": 0.5},
                {"brand": "Competitor", "share": 0.3},
            ],
        },
    )
    db_session.add(batch)
    await db_session.commit()

    with patch("backend.app.routers.dashboard.RedisClient") as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)

        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_experiments"] == 1
    assert data["completed_experiments"] == 1
    assert data["avg_visibility_score"] > 0


@pytest.mark.asyncio
async def test_dashboard_stats_requires_auth(client: TestClient) -> None:
    """Test that dashboard stats endpoint requires authentication."""
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_trends_empty(
    client: TestClient, auth_headers: dict
) -> None:
    """Test trends endpoint with no data returns 30 zero-filled points."""
    with patch("backend.app.routers.dashboard.RedisClient") as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)

        response = client.get("/api/v1/dashboard/trends?days=30", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 30
    # All should be zero when no experiments exist
    for point in data:
        assert point["visibility_rate"] == 0.0
        assert point["share_of_voice"] == 0.0
        assert "date" in point


@pytest.mark.asyncio
async def test_dashboard_trends_days_validation(
    client: TestClient, auth_headers: dict
) -> None:
    """Test trends endpoint validates days parameter."""
    # Too few days
    response = client.get("/api/v1/dashboard/trends?days=3", headers=auth_headers)
    assert response.status_code == 422

    # Too many days
    response = client.get("/api/v1/dashboard/trends?days=200", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_dashboard_trends_requires_auth(client: TestClient) -> None:
    """Test that trends endpoint requires authentication."""
    response = client.get("/api/v1/dashboard/trends")
    assert response.status_code == 401
