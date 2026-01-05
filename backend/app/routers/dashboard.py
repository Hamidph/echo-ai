"""
FastAPI router for dashboard analytics.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, desc
from sqlalchemy.orm import selectinload

from backend.app.core.database import DbSession
from backend.app.core.deps import get_current_active_user
from backend.app.models.experiment import Experiment, ExperimentStatus, BatchRun
from backend.app.models.user import User
from backend.app.schemas.dashboard import (
    DashboardStatsResponse,
    ShareOfVoiceItem,
    DailyVisibility,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


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
    """,
)
async def get_dashboard_stats(
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> DashboardStatsResponse:
    # 1. Basic Counts
    total_query = select(func.count()).where(Experiment.user_id == current_user.id)
    completed_query = select(func.count()).where(
        Experiment.user_id == current_user.id,
        Experiment.status == ExperimentStatus.COMPLETED
    )
    
    total_experiments = (await session.execute(total_query)).scalar() or 0
    completed_experiments = (await session.execute(completed_query)).scalar() or 0

    if completed_experiments == 0:
        return DashboardStatsResponse(
            total_experiments=total_experiments,
            completed_experiments=0,
            avg_visibility_score=0.0,
            share_of_voice=[],
            visibility_trend=[],
        )

    # 2. Fetch completed experiments with their BatchRuns for aggregation
    # We fetch only necessary fields to optimize
    stmt = (
        select(Experiment)
        .options(selectinload(Experiment.batch_runs))
        .where(
            Experiment.user_id == current_user.id,
            Experiment.status == ExperimentStatus.COMPLETED
        )
        .order_by(desc(Experiment.created_at))
        .limit(100)  # Limit aggregation to last 100 for performance MVP
    )
    result = await session.execute(stmt)
    experiments = result.scalars().all()

    # Aggregators
    total_visibility_sum = 0.0
    count_for_avg = 0
    
    sov_agg: dict[str, float] = defaultdict(float)
    sov_count: dict[str, int] = defaultdict(int)
    
    trend_data: dict[str, list[float]] = defaultdict(list)

    for exp in experiments:
        if not exp.batch_runs:
            continue
            
        # Use the latest batch run (or primary one)
        # In this model, an experiment typically has one batch run per provider
        # We will average across all batch runs for this experiment
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
            # Structure: [{'brand': 'Name', 'share': 0.4}, ...]
            sov_list = metrics.get("share_of_voice", [])
            for item in sov_list:
                brand = item.get("brand")
                share = item.get("share", 0.0)
                if brand:
                    sov_agg[brand] += share
                    sov_count[brand] += 1

    # Final Calculations
    
    # 1. Avg Visibility
    avg_vis = (total_visibility_sum / count_for_avg) * 100 if count_for_avg > 0 else 0.0
    
    # 2. SOV
    final_sov = []
    # Normalize SOV - we want the average share per brand across experiments where they appeared
    # But for a pie chart, we usually want "Average Share of Voice distribution"
    # Strategy: Sum up all shares and normalize to 100%? 
    # Better Strategy: Average share for each brand across all experiments. 
    # If a brand is not in an experiment, is its share 0? Yes, implicitly.
    # So we divide by `count_for_avg` (total validated runs)
    
    # However, `competitor_brands` vary per experiment. 
    # Simple approach for MVP: Sum of shares divided by count_for_avg
    if count_for_avg > 0:
        for brand, total_share in sov_agg.items():
            avg_share = (total_share / count_for_avg) * 100
            final_sov.append(ShareOfVoiceItem(brand=brand, percentage=round(avg_share, 1)))
            
    # Sort by percentage desc
    final_sov.sort(key=lambda x: x.percentage, reverse=True)
    
    # 3. Trends
    trends = []
    # Fill last 30 days
    today = datetime.now(timezone.utc).date()
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        
        daily_scores = trend_data.get(d_str, [])
        if daily_scores:
            daily_avg = sum(daily_scores) / len(daily_scores)
            trends.append(DailyVisibility(date=d, visibility_score=round(daily_avg * 100, 1)))
        else:
            # If no data, use 0 or carry forward? 0 is safer for now
            trends.append(DailyVisibility(date=d, visibility_score=0.0))

    return DashboardStatsResponse(
        total_experiments=total_experiments,
        completed_experiments=completed_experiments,
        avg_visibility_score=round(avg_vis, 1),
        share_of_voice=final_sov,
        visibility_trend=trends,
    )
