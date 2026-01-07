
import logging
from typing import Annotated
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from backend.app.core.database import DbSession
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/detailed", summary="Detailed system health status")
async def detailed_health_check(session: DbSession):
    """
    Check connectivity of critical infrastructure components:
    - Database (PostgreSQL)
    - Cache/Broker (Redis)
    """
    settings = get_settings()
    status_report = {
        "status": "healthy",
        "components": {
            "database": "unknown",
            "redis": "unknown",
        }
    }
    
    # 1. Check Database
    try:
        await session.execute(text("SELECT 1"))
        status_report["components"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Health check failed for Database: {e}")
        status_report["components"]["database"] = "unhealthy"
        status_report["status"] = "degraded"

    # 2. Check Redis
    try:
        redis = Redis.from_url(str(settings.redis_url), decode_responses=True)
        await redis.ping()
        await redis.close()
        status_report["components"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Health check failed for Redis: {e}")
        status_report["components"]["redis"] = "unhealthy"
        status_report["status"] = "degraded"
    
    if status_report["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=status_report
        )

    return status_report
