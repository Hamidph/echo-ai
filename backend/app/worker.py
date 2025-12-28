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
    task_time_limit=600,  # 10 minute hard limit
    task_soft_time_limit=540,  # 9 minute soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
)

logger = logging.getLogger(__name__)


def run_async(coro: Any) -> Any:
    """
    Helper to run async code in sync Celery tasks.

    Args:
        coro: Coroutine to execute.

    Returns:
        Result of the coroutine.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


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
    from backend.app.builders.analysis import AnalysisBuilder
    from backend.app.builders.runner import RunnerBuilder
    from backend.app.core.database import get_session_factory
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

    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            # Initialize repositories
            exp_repo = ExperimentRepository(session)
            batch_repo = BatchRunRepository(session)
            iter_repo = IterationRepository(session)

            # Fetch experiment
            experiment = await exp_repo.get_experiment(UUID(experiment_id))
            if not experiment:
                raise ValueError(f"Experiment {experiment_id} not found")

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

            await session.commit()

            # Parse provider enum
            provider_enum = LLMProvider(provider)

            # Build batch configuration from experiment config
            config_dict = experiment.config or {}
            batch_config = BatchConfig(
                iterations=config_dict.get("iterations", 10),
                max_concurrency=config_dict.get("max_concurrency", 10),
                temperature=config_dict.get("temperature", 0.7),
                max_tokens=config_dict.get("max_tokens"),
                model=model or config_dict.get("model"),
                system_prompt=config_dict.get("system_prompt"),
            )

            # Execute the batch run
            logger.info(
                f"Running batch for experiment {experiment_id}: "
                f"{batch_config.iterations} iterations"
            )

            runner = RunnerBuilder()
            batch_result = await runner.run_batch(
                prompt=experiment.prompt,
                provider=provider_enum,
                config=batch_config,
            )

            # Store iteration results
            iterations_data = []
            for iteration in batch_result.iterations:
                iter_data: dict[str, Any] = {
                    "batch_run_id": batch_run.id,
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

            # Run analysis
            logger.info(f"Analyzing results for experiment {experiment_id}")

            target_brands = [experiment.target_brand]
            if experiment.competitor_brands:
                target_brands.extend(experiment.competitor_brands)

            analyzer = AnalysisBuilder()
            analysis_result = analyzer.analyze_batch(
                batch_result=batch_result,
                target_brands=target_brands,
                domain_whitelist=experiment.domain_whitelist,
            )

            # Update batch run with metrics
            await batch_repo.update_batch_status(
                batch_run.id,
                BatchRunStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                duration_ms=batch_result.total_duration_ms,
            )

            await batch_repo.update_batch_metrics(
                batch_run.id,
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

            await session.commit()

            logger.info(
                f"Experiment {experiment_id} completed: "
                f"{batch_result.successful_iterations}/{batch_result.total_iterations} successful"
            )

            return {
                "status": "completed",
                "experiment_id": experiment_id,
                "batch_run_id": str(batch_run.id),
                "task_id": task_id,
                "total_iterations": batch_result.total_iterations,
                "successful_iterations": batch_result.successful_iterations,
                "duration_ms": batch_result.total_duration_ms,
                "metrics": analysis_result.raw_metrics,
            }

        except Exception as e:
            await session.rollback()
            logger.exception(f"Error executing experiment {experiment_id}: {e}")
            raise


async def _mark_experiment_failed(experiment_id: str, error_message: str) -> None:
    """
    Mark an experiment as failed in the database.

    Args:
        experiment_id: UUID of the experiment.
        error_message: Error description.
    """
    from backend.app.core.database import get_session_factory
    from backend.app.models.experiment import ExperimentStatus
    from backend.app.repositories.experiment_repo import ExperimentRepository

    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            exp_repo = ExperimentRepository(session)
            await exp_repo.update_experiment_status(
                UUID(experiment_id),
                ExperimentStatus.FAILED,
                error_message=error_message,
            )
            await session.commit()
        except Exception as e:
            logger.exception(f"Failed to mark experiment {experiment_id} as failed: {e}")


@celery_app.task(name="health_check")  # type: ignore[untyped-decorator]
def health_check_task() -> dict[str, str]:
    """
    Simple health check task for monitoring.

    Returns:
        Dictionary with status.
    """
    return {"status": "healthy", "worker": "ai_visibility"}
