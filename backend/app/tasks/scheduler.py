"""
Scheduler tasks for recurring experiments.
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.app.core.config import get_settings
from backend.app.models.experiment import Experiment, ExperimentStatus, ExperimentFrequency
from backend.app.worker import execute_experiment_task

logger = logging.getLogger(__name__)
settings = get_settings()


async def check_scheduled_experiments() -> dict[str, int]:
    """
    Check for due recurring experiments and trigger them.
    
    1. Find active recurring experiments where next_run_at <= now
    2. For each:
       - Trigger execute_experiment_task for each provider in original config
       - Update last_run_at = now
       - Update next_run_at based on frequency
    """
    engine = create_async_engine(str(settings.database_url))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    triggered_count = 0
    now = datetime.now(timezone.utc)

    try:
        async with session_factory() as session:
            async with session.begin():
                # Find due experiments with their batch runs loaded
                stmt = (
                    select(Experiment)
                    .options(selectinload(Experiment.batch_runs))
                    .where(
                        and_(
                            Experiment.is_recurring == True,
                            Experiment.status != ExperimentStatus.CANCELLED,
                            Experiment.next_run_at <= now
                        )
                    )
                )
                
                result = await session.execute(stmt)
                due_experiments = result.scalars().all()
                
                logger.info(f"Found {len(due_experiments)} due recurring experiments")
                
                for exp in due_experiments:
                    # 1. Trigger Runs
                    # Determine provider from previous batch runs
                    providers = []
                    if exp.batch_runs:
                        # Use the most recent provider(s)
                        # In MVP, usually one provider per experiment
                        # We sort by created_at to get latest
                        latest_run = sorted(exp.batch_runs, key=lambda x: x.created_at, reverse=True)[0]
                        providers = [latest_run.provider]
                    else:
                        # Fallback to config or default
                        providers = exp.config.get("providers", ["openai"])
                        if isinstance(providers, str):
                            providers = [providers]
                        
                    for provider in providers:
                         execute_experiment_task.delay(
                            experiment_id=str(exp.id),
                            provider=provider,
                            model=exp.config.get("model")
                        )
                    
                    # 2. Update Schedule
                    exp.last_run_at = now
                    
                    if exp.frequency == ExperimentFrequency.DAILY:
                        exp.next_run_at = now + timedelta(days=1)
                    elif exp.frequency == ExperimentFrequency.WEEKLY:
                        exp.next_run_at = now + timedelta(weeks=1)
                    elif exp.frequency == ExperimentFrequency.MONTHLY:
                        exp.next_run_at = now + timedelta(days=30)
                    else:
                        # Default to daily if unknown
                        exp.next_run_at = now + timedelta(days=1)
                        
                    triggered_count += 1
                    logger.info(f"Triggered recurring run for Experiment {exp.id}")
            
            # Commit happens here
    
    except Exception as e:
        logger.exception(f"Error checking scheduled experiments: {e}")
    finally:
        await engine.dispose()
        
    return {"triggered": triggered_count}
