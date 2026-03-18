"""
Tests for experiment endpoints.
"""

from datetime import UTC
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import get_password_hash
from backend.app.models.experiment import BatchRun, BatchRunStatus, Experiment, ExperimentStatus
from backend.app.models.user import PricingTier, User, UserRole


@pytest.mark.asyncio
async def test_list_experiments_empty(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test listing experiments when none exist returns empty list."""
    response = client.get("/api/v1/experiments", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["experiments"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_experiments_with_data(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test listing experiments returns user's experiments."""
    exp = Experiment(
        user_id=test_user.id,
        prompt="What is the best CRM for startups?",
        target_brand="TestBrand",
        config={"iterations": 10},
        status=ExperimentStatus.COMPLETED.value,
    )
    db_session.add(exp)
    await db_session.commit()

    response = client.get("/api/v1/experiments", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["experiments"][0]["target_brand"] == "TestBrand"


@pytest.mark.asyncio
async def test_list_experiments_pagination(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test experiment pagination with limit and offset."""
    # Create 5 experiments
    for i in range(5):
        exp = Experiment(
            user_id=test_user.id,
            prompt=f"Prompt {i}",
            target_brand="TestBrand",
            config={"iterations": 10},
            status=ExperimentStatus.COMPLETED.value,
        )
        db_session.add(exp)
    await db_session.commit()

    # Fetch with limit=2
    response = client.get("/api/v1/experiments?limit=2&offset=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["experiments"]) == 2
    assert data["total"] == 5
    assert data["limit"] == 2

    # Fetch page 2
    response2 = client.get("/api/v1/experiments?limit=2&offset=2", headers=auth_headers)
    data2 = response2.json()
    assert len(data2["experiments"]) == 2


@pytest.mark.asyncio
async def test_list_experiments_status_filter(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test experiment status filtering."""
    # Create completed and failed experiments
    for status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]:
        exp = Experiment(
            user_id=test_user.id,
            prompt=f"Prompt {status}",
            target_brand="TestBrand",
            config={"iterations": 10},
            status=status.value,
        )
        db_session.add(exp)
    await db_session.commit()

    # Filter by completed
    response = client.get("/api/v1/experiments?status=completed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["experiments"][0]["status"] == "completed"

    # Filter by failed
    response2 = client.get("/api/v1/experiments?status=failed", headers=auth_headers)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["total"] == 1


@pytest.mark.asyncio
async def test_get_experiment_not_found(client: TestClient, auth_headers: dict) -> None:
    """Test getting a non-existent experiment returns 404."""
    response = client.get(f"/api/v1/experiments/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_experiment_wrong_user(
    client: TestClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    """Test that users cannot access other users' experiments."""
    # Create experiment owned by another user
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("pass"),
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_prompt_quota=3,
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    exp = Experiment(
        user_id=other_user.id,
        prompt="Private prompt",
        target_brand="OtherBrand",
        config={"iterations": 5},
        status=ExperimentStatus.COMPLETED.value,
    )
    db_session.add(exp)
    await db_session.commit()
    await db_session.refresh(exp)

    # Try to access with different user's auth
    response = client.get(f"/api/v1/experiments/{exp.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_experiment_csv(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test exporting experiment data as CSV."""
    from datetime import datetime

    exp = Experiment(
        user_id=test_user.id,
        prompt="Export test prompt",
        target_brand="ExportBrand",
        config={"iterations": 2},
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
        total_iterations=2,
        successful_iterations=2,
        failed_iterations=0,
        total_tokens=100,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )
    db_session.add(batch)
    await db_session.commit()

    response = client.get(
        f"/api/v1/experiments/{exp.id}/export?format=csv",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_export_experiment_json(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test exporting experiment data as JSON."""
    from datetime import datetime

    exp = Experiment(
        user_id=test_user.id,
        prompt="JSON export test",
        target_brand="JSONBrand",
        config={"iterations": 2},
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
        total_iterations=2,
        successful_iterations=2,
        failed_iterations=0,
        total_tokens=100,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )
    db_session.add(batch)
    await db_session.commit()

    response = client.get(
        f"/api/v1/experiments/{exp.id}/export?format=json",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    data = response.json()
    assert data["target_brand"] == "JSONBrand"
    assert "batch_runs" in data


@pytest.mark.asyncio
async def test_export_invalid_format(
    client: TestClient, db_session: AsyncSession, test_user: User, auth_headers: dict
) -> None:
    """Test exporting with an invalid format returns 422."""
    exp = Experiment(
        user_id=test_user.id,
        prompt="Format test",
        target_brand="FormatBrand",
        config={"iterations": 2},
        status=ExperimentStatus.COMPLETED.value,
    )
    db_session.add(exp)
    await db_session.commit()
    await db_session.refresh(exp)

    response = client.get(
        f"/api/v1/experiments/{exp.id}/export?format=xml",
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_create_too_many(client: TestClient, auth_headers: dict) -> None:
    """Test batch creation with more than 10 experiments returns 400."""
    experiments = [
        {
            "prompt": f"Prompt {i} about something interesting",
            "target_brand": "TestBrand",
            "provider": "openai",
            "iterations": 5,
        }
        for i in range(11)
    ]

    response = client.post(
        "/api/v1/experiments/batch",
        json=experiments,
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_create_empty(client: TestClient, auth_headers: dict) -> None:
    """Test batch creation with empty list returns 400."""
    response = client.post(
        "/api/v1/experiments/batch",
        json=[],
        headers=auth_headers,
    )

    assert response.status_code == 400
