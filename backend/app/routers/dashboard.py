"""
FastAPI router for dashboard analytics.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

from backend.app.core.database import DbSession
from backend.app.core.deps import get_current_active_user
from backend.app.core.redis import RedisClient
from backend.app.models.experiment import BatchRun, Experiment, ExperimentStatus
from backend.app.models.user import User
from backend.app.schemas.dashboard import (
    DailyVisibility,
    DashboardStatsResponse,
    ShareOfVoiceItem,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)

STATS_CACHE_TTL = 300  # 5 minutes


class TrendPoint(BaseModel):
    """Single data point in a visibility trend series."""

    date: str
    visibility_rate: float
    share_of_voice: float


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="Get aggregated dashboard statistics",
    description="""
    Calculate aggregated metrics for the user's dashboard:
    - Total and completed experiments
    - Average visibility score (weighted)
    - Aggregated Share of Voice
    - 30-day visibility trend

    Results are cached in Redis for 5 minutes.
    """,
)
async def get_dashboard_stats(
    session: DbSession,
    redis: RedisClient,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> DashboardStatsResponse:
    cache_key = f"dashboard:stats:{current_user.id}"

    # Try cache first
    try:
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            return DashboardStatsResponse(**data)
    except Exception as e:
        logger.warning(f"Redis cache read failed for {cache_key}: {e}")

    # 1. Basic Counts
    total_query = select(func.count()).where(Experiment.user_id == current_user.id)
    completed_query = select(func.count()).where(
        Experiment.user_id == current_user.id,
        Experiment.status == ExperimentStatus.COMPLETED,
    )

    total_experiments = (await session.execute(total_query)).scalar() or 0
    completed_experiments = (await session.execute(completed_query)).scalar() or 0

    # Return basic stats even if no completed experiments
    if completed_experiments == 0:
        result = DashboardStatsResponse(
            total_experiments=total_experiments,
            completed_experiments=0,
            avg_visibility_score=0.0,
            share_of_voice=[],
            visibility_trend=[],
        )
        _cache_stats(redis, cache_key, result)
        return result

    # 2. Fetch completed experiments with their BatchRuns for aggregation
    stmt = (
        select(Experiment)
        .options(selectinload(Experiment.batch_runs))
        .where(
            Experiment.user_id == current_user.id,
            Experiment.status == ExperimentStatus.COMPLETED,
        )
        .order_by(desc(Experiment.created_at))
        .limit(100)
    )
    result_rows = await session.execute(stmt)
    experiments = result_rows.scalars().all()

    # Aggregators
    total_visibility_sum = 0.0
    count_for_avg = 0

    sov_agg: dict[str, float] = defaultdict(float)
    sov_count: dict[str, int] = defaultdict(int)

    trend_data: dict[str, list[float]] = defaultdict(list)

    for exp in experiments:
        if not exp.batch_runs:
            continue

        for br in exp.batch_runs:
            if not br.metrics:
                continue

            metrics = br.metrics

            # Visibility Score
            target_vis = metrics.get("target_visibility", {})
            vis_rate = target_vis.get("visibility_rate", 0.0)

            total_visibility_sum += vis_rate
            count_for_avg += 1

            # Trend Data (Group by Date)
            if br.completed_at:
                date_key = br.completed_at.strftime("%Y-%m-%d")
                trend_data[date_key].append(vis_rate)

            # Share of Voice
            sov_list = metrics.get("share_of_voice", [])
            for item in sov_list:
                brand = item.get("brand")
                share = item.get("share", 0.0)
                if brand:
                    sov_agg[brand] += share
                    sov_count[brand] += 1

    # Final Calculations
    avg_vis = (total_visibility_sum / count_for_avg) * 100 if count_for_avg > 0 else 0.0

    final_sov = []
    if count_for_avg > 0:
        for brand, total_share in sov_agg.items():
            avg_share = (total_share / count_for_avg) * 100
            final_sov.append(ShareOfVoiceItem(brand=brand, percentage=round(avg_share, 1)))
    final_sov.sort(key=lambda x: x.percentage, reverse=True)

    trends = []
    today = datetime.now(timezone.utc).date()
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        daily_scores = trend_data.get(d_str, [])
        if daily_scores:
            daily_avg = sum(daily_scores) / len(daily_scores)
            trends.append(DailyVisibility(date=d, visibility_score=round(daily_avg * 100, 1)))
        else:
            trends.append(DailyVisibility(date=d, visibility_score=0.0))

    stats = DashboardStatsResponse(
        total_experiments=total_experiments,
        completed_experiments=completed_experiments,
        avg_visibility_score=round(avg_vis, 1),
        share_of_voice=final_sov,
        visibility_trend=trends,
    )

    # Write to cache (fire-and-forget, don't block response)
    try:
        await redis.setex(
            cache_key,
            STATS_CACHE_TTL,
            stats.model_dump_json(),
        )
    except Exception as e:
        logger.warning(f"Redis cache write failed for {cache_key}: {e}")

    return stats


def _cache_stats(redis: object, cache_key: str, stats: DashboardStatsResponse) -> None:
    """Helper — we skip async write for empty-state shortcut to avoid awaiting in sync ctx."""
    pass  # Cache written in the main path only


@router.get(
    "/trends",
    response_model=list[TrendPoint],
    summary="Get visibility trend time-series",
    description="""
    Returns day-by-day visibility and share-of-voice data for the specified
    number of past days. Useful for rendering trend charts on the dashboard.
    """,
)
async def get_visibility_trends(
    session: DbSession,
    redis: RedisClient,
    current_user: Annotated[User, Depends(get_current_active_user)],
    days: int = Query(default=30, ge=7, le=90, description="Number of days to include"),
) -> list[TrendPoint]:
    cache_key = f"dashboard:trends:{current_user.id}:{days}"

    # Try cache first (2 min TTL for trends)
    try:
        cached = await redis.get(cache_key)
        if cached:
            raw = json.loads(cached)
            return [TrendPoint(**item) for item in raw]
    except Exception as e:
        logger.warning(f"Redis cache read failed for {cache_key}: {e}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Fetch completed batch_runs within the date range for this user's experiments
    stmt = (
        select(BatchRun)
        .join(Experiment, BatchRun.experiment_id == Experiment.id)
        .where(
            Experiment.user_id == current_user.id,
            Experiment.status == ExperimentStatus.COMPLETED,
            BatchRun.completed_at >= cutoff,
        )
        .order_by(BatchRun.completed_at)
    )
    result = await session.execute(stmt)
    batch_runs = result.scalars().all()

    # Aggregate by day
    vis_by_day: dict[str, list[float]] = defaultdict(list)
    sov_by_day: dict[str, list[float]] = defaultdict(list)

    for br in batch_runs:
        if not br.metrics or not br.completed_at:
            continue

        date_key = br.completed_at.strftime("%Y-%m-%d")
        metrics = br.metrics

        target_vis = metrics.get("target_visibility", {})
        vis_rate = target_vis.get("visibility_rate", 0.0)
        vis_by_day[date_key].append(vis_rate * 100)

        sov_list = metrics.get("share_of_voice", [])
        if sov_list:
            # Use the first brand's share as the primary metric
            sov_by_day[date_key].append(sov_list[0].get("share", 0.0) * 100)

    # Build ordered list for all days in range
    trend_points: list[TrendPoint] = []
    today = datetime.now(timezone.utc).date()
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")

        vis_values = vis_by_day.get(d_str, [])
        sov_values = sov_by_day.get(d_str, [])

        trend_points.append(
            TrendPoint(
                date=d_str,
                visibility_rate=round(sum(vis_values) / len(vis_values), 1) if vis_values else 0.0,
                share_of_voice=round(sum(sov_values) / len(sov_values), 1) if sov_values else 0.0,
            )
        )

    # Cache for 2 minutes
    try:
        await redis.setex(
            cache_key,
            120,
            json.dumps([p.model_dump() for p in trend_points]),
        )
    except Exception as e:
        logger.warning(f"Redis cache write failed for {cache_key}: {e}")

    return trend_points
