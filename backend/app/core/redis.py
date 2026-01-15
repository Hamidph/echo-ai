"""
Redis connection management for caching and Celery broker.

This module provides async Redis client configuration and connection
management for the platform's caching and task queue needs.

Innovation: Redis serves dual purpose - Celery broker for distributed
task processing and cache for probabilistic result memoization.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from redis.asyncio import Redis

from backend.app.core.config import Settings, get_settings


def create_redis_client(settings: Settings) -> Redis:  # type: ignore[type-arg]
    """
    Create an async Redis client with connection pooling.

    Args:
        settings: Application settings containing Redis configuration.

    Returns:
        Redis: Configured async Redis client.
    """
    return aioredis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=5,    # Add 5 second connection timeout
        socket_timeout=5,             # Add 5 second operation timeout
        retry_on_timeout=True,        # Retry on timeout
    )


# Module-level instance (initialized lazily)
_redis_client: Redis | None = None  # type: ignore[type-arg]


def get_redis_client() -> Redis:  # type: ignore[type-arg]
    """
    Get or create the Redis client singleton.

    Returns:
        Redis: The Redis client instance.
    """
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = create_redis_client(settings)
    return _redis_client


async def get_redis() -> AsyncGenerator[Redis, None]:  # type: ignore[type-arg]
    """
    FastAPI dependency for Redis client injection.

    Yields the async Redis client for use in route handlers.

    Yields:
        Redis: An async Redis client.
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        # Connection pooling handles cleanup automatically
        pass


async def close_redis_connection() -> None:
    """
    Close the Redis connection pool.

    Should be called during application shutdown to cleanly
    release all Redis connections.
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def check_redis_health() -> bool:
    """
    Check if Redis connection is healthy.

    Returns:
        bool: True if Redis is reachable and responding.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        client = get_redis_client()
        # Use asyncio.wait_for to add timeout
        import asyncio
        await asyncio.wait_for(client.ping(), timeout=3.0)
        return True
    except asyncio.TimeoutError:
        logger.warning("Redis health check timed out after 3 seconds")
        return False
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


# Type alias for dependency injection
RedisClient = Annotated[Redis, Depends(get_redis)]
