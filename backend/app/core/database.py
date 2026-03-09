"""
Database connection and session management using SQLAlchemy 2.0 async.

This module provides the async database engine, session factory, and
dependency injection for FastAPI routes.

Innovation: Uses async SQLAlchemy for non-blocking database operations,
enabling high-concurrency probabilistic workloads.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import Settings, get_settings


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all ORM models.

    All database models should inherit from this class to ensure
    proper table creation and relationship management.
    """

    pass


def create_database_engine(settings: Settings) -> AsyncEngine:
    """
    Create an async SQLAlchemy engine with connection pooling.

    Args:
        settings: Application settings containing database configuration.

    Returns:
        AsyncEngine: Configured async database engine.
    """
    return create_async_engine(
        str(settings.database_url),
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_timeout=30,
        pool_use_lifo=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create an async session factory for database connections.

    Args:
        engine: The async database engine.

    Returns:
        async_sessionmaker: Factory for creating async database sessions.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# Module-level instances (initialized lazily)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the database engine singleton.

    Returns:
        AsyncEngine: The database engine instance.
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_database_engine(settings)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the session factory singleton.

    Returns:
        async_sessionmaker: The session factory instance.
    """
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = create_session_factory(engine)
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.

    Yields an async database session and ensures proper cleanup
    after the request is complete.

    Yields:
        AsyncSession: An async database session.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# Backward compatibility alias
get_db = get_db_session
