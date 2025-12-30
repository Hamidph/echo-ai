"""
Pytest configuration and fixtures for the test suite.

This module provides shared fixtures for database sessions,
test clients, and mock LLM providers.
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.core.database import Base, get_db
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.main import app
from backend.app.models.user import User, UserRole, PricingTier

# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def client() -> TestClient:
    """
    Provide a synchronous test client for FastAPI.

    Returns:
        TestClient: A test client instance.
    """
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an asynchronous test client for FastAPI.

    Yields:
        AsyncClient: An async test client instance.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def mock_settings() -> dict[str, Any]:
    """
    Provide mock settings for testing.

    Returns:
        dict: Mock configuration values.
    """
    return {
        "app_name": "Test Platform",
        "app_version": "0.0.1",
        "environment": "development",
        "debug": True,
        "default_iterations": 5,
        "max_iterations": 10,
        "confidence_level": 0.95,
    }


@pytest.fixture
async def db_engine() -> AsyncGenerator[Any, None]:
    """
    Provide a test database engine.

    Yields:
        Engine: SQLAlchemy async engine for testing.
    """
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: Any) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a test database session.

    Args:
        db_engine: The test database engine.

    Yields:
        AsyncSession: Database session for testing.
    """
    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create a test user.

    Args:
        db_session: Database session.

    Returns:
        User: A test user instance.
    """
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_iteration_quota=100,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """
    Provide authentication headers for testing.

    Args:
        test_user: The test user.

    Returns:
        dict: Headers with Bearer token.
    """
    token = create_access_token(data={"user_id": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}

