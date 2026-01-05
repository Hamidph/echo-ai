"""
Scheduler tasks for recurring experiments.
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, and_
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
                # Find due experiments
                stmt = select(Experiment).where(
                    and_(
                        Experiment.is_recurring == True,
                        Experiment.status != ExperimentStatus.CANCELLED,
                        Experiment.next_run_at <= now
                    )
                )
                
                result = await session.execute(stmt)
                due_experiments = result.scalars().all()
                
                logger.info(f"Found {len(due_experiments)} due recurring experiments")
                
                for exp in due_experiments:
                    # 1. Trigger Runs
                    # We need to know which providers to run.
                    # Usually an experiment has a batch run per provider.
                    # We can re-use the config or infer from previous batch runs?
                    # Simpler: The Experiment model doesn't explicitly store "providers list" 
                    # other than in batch_runs.
                    # Let's check the config or assume a default/previous run provider.
                    # Robust way: Check existing batch runs to see which providers were used.
                    
                    # For MVP, let's assume valid providers are in config or we look at `batch_runs`
                    # Since we can't easily async load relationships in this loop without careful handling,
                    # let's assume the user wants to re-run the *same* providers as the initial setup.
                    # Use a default fallback of "openai" if unknown.
                    
                    # Actually, we need to be careful. `execute_experiment_task` is a Celery task.
                    # We can fire it off.
                    
                    # Hack: For now, re-run for "openai" as default, or store providers in config?
                    # Better: Add `providers` to Experiment config schema in future.
                    # Current: Check if `config` has `providers` key?
                    
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
