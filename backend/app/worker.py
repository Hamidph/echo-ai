"""
Celery worker for background experiment execution.

This module defines the Celery application and background tasks for
running probabilistic experiments asynchronously.

Innovation: Using Celery for background processing enables the platform
to handle long-running Monte Carlo simulations (50-100 iterations) without
blocking the API. This distributed architecture is essential for scaling
to thousands of concurrent experiments.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from celery import Celery

from backend.app.core.config import get_settings

# Initialize Celery app
settings = get_settings()

celery_app = Celery(
    "ai_visibility",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit (allows for large batches)
    task_soft_time_limit=3300,  # 55 minute soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "check-scheduled-experiments-every-hour": {
        "task": "check_scheduled_experiments",
        "schedule": 3600.0,  # Run every hour
    },
    "cleanup-old-pii-data-daily": {
        "task": "cleanup_old_pii_data",
        "schedule": 86400.0,  # Run every 24 hours (daily)
    },
}

logger = logging.getLogger(__name__)


def run_async(coro: Any) -> Any:
    """
    Helper to run async code in sync Celery tasks.

    Uses asyncio.run() which properly manages event loop lifecycle,
    preventing connection pool corruption and memory leaks.

    Args:
        coro: Coroutine to execute.

    Returns:
        Result of the coroutine.
    """
    return asyncio.run(coro)


@celery_app.task(bind=True, name="execute_experiment")  # type: ignore[untyped-decorator]
def execute_experiment_task(
    self: Any,
    experiment_id: str,
    provider: str,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Execute a probabilistic experiment as a background task.

    This task orchestrates the full experiment lifecycle:
    1. Fetch experiment configuration from database
    2. Initialize RunnerBuilder and execute batch
    3. Analyze results with AnalysisBuilder
    4. Save results back to database

    Innovation: This task encapsulates the entire "Probabilistic Visibility
    Analysis" pipeline, enabling fire-and-forget experiment execution.
    The task ID serves as a job reference for status polling.

    Args:
        self: Celery task instance (for task_id access).
        experiment_id: UUID of the experiment to execute.
        provider: LLM provider to use (openai, anthropic, perplexity).
        model: Optional model override.

    Returns:
        Dictionary with execution status and metrics.
    """
    logger.info(f"Starting experiment {experiment_id} with provider {provider}")

    try:
        result: dict[str, Any] = run_async(
            _execute_experiment_async(
                experiment_id=experiment_id,
                provider=provider,
                model=model,
                task_id=self.request.id,
            )
        )
        return result
    except Exception as e:
        logger.exception(f"Experiment {experiment_id} failed: {e}")
        # Update experiment status to failed
        run_async(_mark_experiment_failed(experiment_id, str(e)))
        raise


async def _execute_experiment_async(
    experiment_id: str,
    provider: str,
    model: str | None,
    task_id: str | None,
) -> dict[str, Any]:
    """
    Async implementation of experiment execution.

    Args:
        experiment_id: UUID of the experiment.
        provider: LLM provider name.
        model: Optional model override.
        task_id: Celery task ID for tracking.

    Returns:
        Dictionary with execution results.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from backend.app.builders.analysis import AnalysisBuilder
    from backend.app.builders.runner import RunnerBuilder
    # Import User first to ensure relationship mapping works
    from backend.app.models.user import User  # noqa: F401
    from backend.app.models.experiment import (
        BatchRunStatus,
        ExperimentStatus,
    )
    from backend.app.repositories.experiment_repo import (
        BatchRunRepository,
        ExperimentRepository,
        IterationRepository,
    )
    from backend.app.schemas.llm import LLMProvider
    from backend.app.schemas.runner import BatchConfig, IterationStatus

    # Create a fresh engine for this task to avoid event loop conflicts
    # Use smaller pool size to prevent connection exhaustion
    engine = create_async_engine(
        str(settings.database_url),
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=3,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Variables for refund logic
    iterations_count = None
    user_id = None

    # Use a single atomic transaction for the entire operation
    try:
        async with session_factory() as session:
                # Phase 1: Start Experiment (Transaction 1)
                async with session.begin():
                    # Initialize repositories
                    exp_repo = ExperimentRepository(session)
                    batch_repo = BatchRunRepository(session)
                    
                    # Fetch experiment
                    experiment = await exp_repo.get_experiment(UUID(experiment_id))
                    if not experiment:
                        raise ValueError(f"Experiment {experiment_id} not found")
                    
                    # Capture refund details early
                    user_id = experiment.user_id
                    config_dict = experiment.config or {}
                    iterations_count = config_dict.get("iterations", 10)

                    # Update experiment status to running
                    await exp_repo.update_experiment_status(
                        UUID(experiment_id),
                        ExperimentStatus.RUNNING,
                    )


                    # Create batch run record
                    batch_run = await batch_repo.create_batch_run(
                        experiment_id=UUID(experiment_id),
                        provider=provider,
                        model=model or "default",
                    )

                    # Update batch status to running
                    await batch_repo.update_batch_status(
                        batch_run.id,
                        BatchRunStatus.RUNNING,
                        started_at=datetime.utcnow(),
                    )
                    
                    # Store needed data for next phases
                    batch_run_id = batch_run.id
                    # user_id & iterations_count already captured
                    
                    prompt = experiment.prompt
                    target_brand = experiment.target_brand
                    competitor_brands = experiment.competitor_brands
                    domain_whitelist = experiment.domain_whitelist
                    
                    # Parse provider enum
                    provider_enum = LLMProvider(provider)

                    # Build batch configuration
                    batch_config = BatchConfig(
                        iterations=iterations_count,
                        max_concurrency=config_dict.get("max_concurrency", 10),
                        temperature=config_dict.get("temperature", 0.7),
                        max_tokens=config_dict.get("max_tokens"),
                        model=model or config_dict.get("model"),
                        system_prompt=config_dict.get("system_prompt"),
                    )

                # Phase 2: Execute Batch (No DB Lock)
                # Transaction 1 committed. Connection returned to pool (briefly).
                logger.info(
                    f"Running batch for experiment {experiment_id}: "
                    f"{batch_config.iterations} iterations"
                )

                runner = RunnerBuilder()
                batch_result = await runner.run_batch(
                    prompt=prompt,
                    provider=provider_enum,
                    config=batch_config,
                )

                # Phase 3: Save Iterations (Transaction 2)
                async with session.begin():
                    # Re-init repositories for new transaction scope
                    iter_repo = IterationRepository(session)
                    
                    iterations_data = []
                    for iteration in batch_result.iterations:
                        iter_data: dict[str, Any] = {
                            "batch_run_id": batch_run_id,
                            "iteration_index": iteration.iteration_index,
                            "is_success": iteration.status == IterationStatus.SUCCESS,
                            "status": iteration.status.value,
                            "latency_ms": iteration.latency_ms,
                            "error_message": iteration.error_message,
                        }

                        if iteration.response:
                            iter_data["raw_response"] = iteration.response.content
                            if iteration.response.usage:
                                iter_data["prompt_tokens"] = iteration.response.usage.prompt_tokens
                                iter_data["completion_tokens"] = iteration.response.usage.completion_tokens
                                iter_data["total_tokens"] = iteration.response.usage.total_tokens

                        iterations_data.append(iter_data)

                    await iter_repo.bulk_create_iterations(iterations_data)

                # Phase 4: Analyze (No DB Lock)
                logger.info(f"Analyzing results for experiment {experiment_id}")

                target_brands_list = [target_brand]
                if competitor_brands:
                    target_brands_list.extend(competitor_brands)

                analyzer = AnalysisBuilder()
                analysis_result = analyzer.analyze_batch(
                    batch_result=batch_result,
                    target_brands=target_brands_list,
                    domain_whitelist=domain_whitelist,
                )

                # Phase 5: Save Metrics & Finish (Transaction 3)
                async with session.begin():
                    # Re-init repositories
                    batch_repo = BatchRunRepository(session)
                    exp_repo = ExperimentRepository(session)
                    
                    # Update batch run with metrics
                    await batch_repo.update_batch_status(
                        batch_run_id,
                        BatchRunStatus.COMPLETED,
                        completed_at=datetime.utcnow(),
                        duration_ms=batch_result.total_duration_ms,
                    )

                    await batch_repo.update_batch_metrics(
                        batch_run_id,
                        metrics=analysis_result.raw_metrics,
                        total_iterations=batch_result.total_iterations,
                        successful_iterations=batch_result.successful_iterations,
                        failed_iterations=batch_result.failed_iterations,
                        total_tokens=batch_result.total_tokens,
                    )

                    # Update experiment status to completed
                    await exp_repo.update_experiment_status(
                        UUID(experiment_id),
                        ExperimentStatus.COMPLETED,
                    )

                logger.info(
                    f"Experiment {experiment_id} completed: "
                    f"{batch_result.successful_iterations}/{batch_result.total_iterations} successful"
                )

                result = {
                    "status": "completed",
                    "experiment_id": experiment_id,
                    "batch_run_id": str(batch_run_id),
                    "task_id": task_id,
                    "total_iterations": batch_result.total_iterations,
                    "successful_iterations": batch_result.successful_iterations,
                    "duration_ms": batch_result.total_duration_ms,
                    "metrics": analysis_result.raw_metrics,
                }

    except Exception as e:
        logger.exception(f"Error executing experiment {experiment_id}: {e}")
        
        # Mark experiment as failed and issue refund
        # Use captured variables (initialized to None if failure happened before capture)
        run_async(_mark_experiment_failed(
            experiment_id=experiment_id, 
            error_message=str(e),
            refund_amount=iterations_count,
            user_id=user_id
        ))
        raise

    finally:
        # Dispose engine to clean up connections
        await engine.dispose()

async def _refund_user_quota(session: Any, user_id: UUID, amount: int) -> None:
    """Refunding user quota after system failure."""
    from backend.app.repositories.user_repo import UserRepository
    try:
        user_repo = UserRepository(session)
        user = await user_repo.get(user_id)
        if user:
            # decrement usage, ensuring we don't go below 0
            new_usage = max(0, user.prompts_used_this_month - amount)
            await user_repo.update(user_id, prompts_used_this_month=new_usage)
            logger.info(f"Refunded {amount} quota to user {user_id}. New usage: {new_usage}")
    except Exception as e:
        logger.error(f"Failed to refund quota to user {user_id}: {e}")


async def _mark_experiment_failed_internal(
    session: Any,
    experiment_id: str,
    error_message: str,
    refund_amount: int | None = None,
    user_id: UUID | None = None,
) -> None:
    """
    Mark an experiment as failed using an existing session.

    Args:
        session: Active database session.
        experiment_id: UUID of the experiment.
        error_message: Error description.
        refund_amount: Optional amount of quota to refund.
        user_id: User ID for refund.
    """
    from backend.app.models.experiment import ExperimentStatus
    from backend.app.repositories.experiment_repo import ExperimentRepository

    try:
        async with session.begin():
            exp_repo = ExperimentRepository(session)
            await exp_repo.update_experiment_status(
                UUID(experiment_id),
                ExperimentStatus.FAILED,
                error_message=error_message,
            )
            
            # Process refund if applicable
            if refund_amount and user_id and refund_amount > 0:
                await _refund_user_quota(session, user_id, refund_amount)
                
    except Exception as e:
        logger.exception(f"Failed to mark experiment {experiment_id} as failed: {e}")


async def _mark_experiment_failed(
    experiment_id: str, 
    error_message: str,
    refund_amount: int | None = None,
    user_id: UUID | None = None,
) -> None:
    """
    Mark an experiment as failed in the database (standalone function).

    Args:
        experiment_id: UUID of the experiment.
        error_message: Error description.
        refund_amount: Optional quota refund.
        user_id: User ID for refund.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    # Create a fresh engine for this task to avoid event loop conflicts
    engine = create_async_engine(
        str(settings.database_url),
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=5,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        await _mark_experiment_failed_internal(
            session, 
            experiment_id, 
            error_message, 
            refund_amount=refund_amount, 
            user_id=user_id
        )

    # Dispose engine to clean up connections
    await engine.dispose()


@celery_app.task(name="health_check")  # type: ignore[untyped-decorator]
def health_check_task() -> dict[str, str]:
    """
    Simple health check task for monitoring.

    Returns:
        Dictionary with status.
    """
    return {"status": "healthy", "worker": "ai_visibility"}
@celery_app.task(name="check_scheduled_experiments")  # type: ignore[untyped-decorator]
def check_scheduled_experiments_task() -> dict[str, int]:
    """
    Periodic task to check and run scheduled experiments.
    """
    from backend.app.tasks.scheduler import check_scheduled_experiments
    
    logger.info("Checking for scheduled experiments...")
    try:
        result = run_async(check_scheduled_experiments())
        return result
    except Exception as e:
        logger.exception(f"Scheduler task failed: {e}")
        return {"triggered": 0, "error": str(e)}


@celery_app.task(name="cleanup_old_pii_data")  # type: ignore[untyped-decorator]
def cleanup_old_pii_data_task() -> str:
    """
    Periodic task to clean up old PII data.
    """
    from backend.app.tasks.maintenance import cleanup_old_pii_data
    
    logger.info("Starting scheduled PII data cleanup...")
    try:
        result = run_async(cleanup_old_pii_data())
        return result
    except Exception as e:
        logger.exception(f"PII cleanup task failed: {e}")
        return f"Error: {e}"
