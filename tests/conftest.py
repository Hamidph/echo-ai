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

from backend.app.core.database import Base, get_db_session as get_db
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.main import app
from backend.app.models.user import User, UserRole, PricingTier

# Test database URL (use PostgreSQL for testing - matches production)
# SQLite doesn't support JSONB columns used in our models
# Using credentials from .env for local dev compatibility
TEST_DATABASE_URL = "postgresql+asyncpg://hamid:@localhost:5432/ai_visibility_test"


@pytest.fixture
def client() -> TestClient:
    """
    Provide a synchronous test client for FastAPI.

    Returns:
        TestClient: A test client instance.
    """
    # Override dependency with mock settings
    from backend.app.core.config import get_settings, Settings
    
    # Mock settings that point to TEST database
    def get_test_settings() -> Settings:
        return Settings(
            environment="development",
            postgres_db="ai_visibility_test",
            # We must set other Postgres fields if they differ from defaults/env
            # Assuming env vars might interfere, best to be explicit
            postgres_user="hamid",
            postgres_password="",
            postgres_host="localhost",
            postgres_port=5432,
            # IMPORTANT: Disable raw database url to ensure component build is used
            raw_database_url=None, 
        )

    # Force override of the global engine in database module
    from backend.app.core import database
    
    # 1. Clear existing engine if any
    if database._engine:
        # We can't await dispose here easily in sync fixture without loop access
        # but for tests strictly running, we just swap it.
        # Ideally we should clean up, but this is a pragmatic fix.
        pass
    
    # 2. Create new engine with TEST settings and NullPool to avoid connection leaks in tests
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import NullPool
    
    database._engine = create_async_engine(
        str(get_test_settings().database_url),
        echo=get_test_settings().debug,
        poolclass=NullPool,
    )
    
    # 3. Also clear session factory so it recreates with new engine
    database._session_factory = None
    
    # 4. Override dependency for good measure (though get_db uses globals we just swapped)
    app.dependency_overrides[get_settings] = get_test_settings
    
    yield TestClient(app)

    # Teardown: Reset global engine to prevent event loop issues
    database._engine = None
    database._session_factory = None
    app.dependency_overrides.clear()


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
        print("\n[CONFTEST] Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("[CONFTEST] Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("[CONFTEST] Tables created.")

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
        monthly_prompt_quota=100,  # Correct field name
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

