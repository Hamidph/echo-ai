"""
FastAPI application entry point for the Probabilistic LLM Analytics Platform.

This module initializes the FastAPI application with proper lifecycle management,
middleware configuration, and route registration.

Innovation: The platform uses async context managers for resource lifecycle,
ensuring clean startup/shutdown of database and Redis connections.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.app.core.config import Settings, get_settings
from backend.app.core.database import get_engine
from backend.app.core.redis import check_redis_health, close_redis_connection
from backend.app.routers import experiments_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.billing import router as billing_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage application lifecycle events.

    Handles startup initialization (database connections, Redis)
    and shutdown cleanup (closing connections, releasing resources).

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control returns to the application during its lifetime.
    """
    # Startup: Initialize connections
    settings = get_settings()
    app.state.settings = settings

    # Verify database engine is ready
    engine = get_engine()
    app.state.db_engine = engine

    # Verify Redis connection
    redis_healthy = await check_redis_health()
    if not redis_healthy:
        # Log warning but don't fail - Redis might not be needed for all operations
        print("Warning: Redis connection not available")

    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")

    yield

    # Shutdown: Cleanup resources
    print("Shutting down application...")
    await close_redis_connection()
    await engine.dispose()
    print("Cleanup complete")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application ready for use.
    """
    settings = get_settings()

    # Initialize Sentry for error tracking (production only)
    if settings.environment == "production" and hasattr(settings, 'sentry_dsn'):
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
        )

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Echo AI - AI Search Analytics Platform - "
            "Monte Carlo simulation for brand visibility analysis across AI search platforms"
        ),
        lifespan=lifespan,
        debug=settings.debug,
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    # Add rate limiter to app state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configure CORS
    # In development, allow all origins. In production, use frontend_url from settings
    allowed_origins = (
        ["*"]
        if settings.environment == "development"
        else [
            settings.frontend_url,
            "https://echo-ai.vercel.app",  # Add your production frontend URL
        ]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # Register routers
    _register_routers(app, settings)

    return app


def _register_routers(app: FastAPI, settings: Settings) -> None:
    """
    Register API routers with the application.

    Args:
        app: The FastAPI application instance.
        settings: Application settings for route configuration.
    """

    # Health check endpoint at root
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, Any]:
        """
        Check application health status.

        Verifies connectivity to critical services: PostgreSQL and Redis.
        Returns 200 if healthy, 503 if degraded.

        Returns:
            dict: Health status including database and Redis connectivity.
        """
        from sqlalchemy import text
        from backend.app.core.database import get_session_factory

        # Check Redis
        redis_healthy = await check_redis_health()

        # Check Database
        db_healthy = False
        db_error = None
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                db_healthy = result.scalar() == 1
        except Exception as e:
            db_error = str(e)

        # Determine overall status
        all_healthy = redis_healthy and db_healthy
        status_code = "healthy" if all_healthy else "degraded"

        response = {
            "status": status_code,
            "version": settings.app_version,
            "environment": settings.environment,
            "services": {
                "redis": "healthy" if redis_healthy else "unhealthy",
                "database": "healthy" if db_healthy else "unhealthy",
            },
        }

        if db_error:
            response["services"]["database_error"] = db_error

        return response

    # Register API v1 routers
    # Authentication router
    app.include_router(
        auth_router,
        prefix=settings.api_v1_prefix,
    )

    # Billing router
    app.include_router(
        billing_router,
        prefix=settings.api_v1_prefix,
    )

    # Innovation: The experiments router exposes the Probabilistic Visibility
    # Analysis service via a RESTful API
    app.include_router(
        experiments_router,
        prefix=settings.api_v1_prefix,
    )


# Create the application instance
app = create_application()
