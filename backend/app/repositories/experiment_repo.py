"""
Repository for experiment data access operations.

This module implements the Repository pattern for Experiment, BatchRun,
and Iteration models, providing a clean abstraction over database operations.

Innovation: The repository pattern decouples business logic from data access,
enabling testability and flexibility. Async operations ensure non-blocking
database access for high-concurrency probabilistic workloads.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.experiment import (
    BatchRun,
    BatchRunStatus,
    Experiment,
    ExperimentStatus,
    Iteration,
)


class ExperimentRepository:
    """
    Repository for Experiment CRUD operations.

    Provides async methods for creating, reading, and updating experiments
    and their associated batch runs and iterations.

    Innovation: This repository abstracts all database operations, ensuring
    that business logic in builders and routes remains clean and testable.
    The async implementation enables efficient handling of concurrent requests.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository with a database session.

        Args:
            session: Async SQLAlchemy session for database operations.
        """
        self.session = session

    async def create_experiment(
        self,
        user_id: UUID,
        prompt: str,
        target_brand: str,
        config: dict[str, Any],
        competitor_brands: list[str] | None = None,
        domain_whitelist: list[str] | None = None,
    ) -> Experiment:
        """
        Create a new experiment.

        Args:
            user_id: ID of the user creating this experiment.
            prompt: The prompt to analyze.
            target_brand: Primary brand to track visibility for.
            config: Experiment configuration (iterations, temperature, etc.).
            competitor_brands: Optional list of competitor brands.
            domain_whitelist: Optional list of allowed domains for hallucination check.

        Returns:
            Experiment: The created experiment instance.
        """
        experiment = Experiment(
            user_id=user_id,
            prompt=prompt,
            target_brand=target_brand,
            competitor_brands=competitor_brands,
            domain_whitelist=domain_whitelist,
            config=config,
            status=ExperimentStatus.PENDING.value,
        )
        self.session.add(experiment)
        await self.session.flush()
        await self.session.refresh(experiment)
        return experiment

    async def get_experiment(self, experiment_id: UUID) -> Experiment | None:
        """
        Get an experiment by ID.

        Args:
            experiment_id: The experiment UUID.

        Returns:
            Experiment or None if not found.
        """
        stmt = select(Experiment).where(Experiment.id == experiment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_experiment_with_results(
        self,
        experiment_id: UUID,
    ) -> Experiment | None:
        """
        Get an experiment with all related batch runs and iterations.

        This method eagerly loads all related data for complete result retrieval.

        Args:
            experiment_id: The experiment UUID.

        Returns:
            Experiment with loaded relationships, or None if not found.
        """
        stmt = (
            select(Experiment)
            .where(Experiment.id == experiment_id)
            .options(selectinload(Experiment.batch_runs).selectinload(BatchRun.iterations))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_experiment_status(
        self,
        experiment_id: UUID,
        status: ExperimentStatus,
        error_message: str | None = None,
    ) -> None:
        """
        Update the status of an experiment.

        Args:
            experiment_id: The experiment UUID.
            status: New status value.
            error_message: Optional error message if status is FAILED.
        """
        stmt = (
            update(Experiment)
            .where(Experiment.id == experiment_id)
            .values(
                status=status.value,
                error_message=error_message,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)

    async def list_experiments(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: ExperimentStatus | None = None,
    ) -> list[Experiment]:
        """
        List experiments for a specific user with pagination and optional status filter.

        Args:
            user_id: Filter experiments by this user ID.
            limit: Maximum number of experiments to return.
            offset: Number of experiments to skip.
            status: Optional status filter.

        Returns:
            List of experiments belonging to the user.
        """
        stmt = (
            select(Experiment)
            .where(Experiment.user_id == user_id)
            .order_by(Experiment.created_at.desc())
        )

        if status:
            stmt = stmt.where(Experiment.status == status.value)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_experiments(
        self,
        user_id: UUID,
        status: ExperimentStatus | None = None,
    ) -> int:
        """
        Count total experiments for a user with optional status filter.

        Args:
            user_id: Filter experiments by this user ID.
            status: Optional status filter.

        Returns:
            Total count of experiments.
        """
        from sqlalchemy import func
        
        stmt = (
            select(func.count())
            .select_from(Experiment)
            .where(Experiment.user_id == user_id)
        )

        if status:
            stmt = stmt.where(Experiment.status == status.value)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_experiment_by_user(
        self,
        experiment_id: UUID,
        user_id: UUID,
    ) -> Experiment | None:
        """
        Get an experiment by ID, ensuring it belongs to the specified user.

        Args:
            experiment_id: The experiment UUID.
            user_id: The user UUID who should own this experiment.

        Returns:
            Experiment or None if not found or doesn't belong to user.
        """
        stmt = select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class BatchRunRepository:
    """
    Repository for BatchRun CRUD operations.

    Innovation: Separating batch run operations enables fine-grained control
    over the execution lifecycle and metrics storage.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    async def create_batch_run(
        self,
        experiment_id: UUID,
        provider: str,
        model: str,
    ) -> BatchRun:
        """
        Create a new batch run for an experiment.

        Args:
            experiment_id: Parent experiment UUID.
            provider: LLM provider name.
            model: Model identifier.

        Returns:
            BatchRun: The created batch run instance.
        """
        batch_run = BatchRun(
            experiment_id=experiment_id,
            provider=provider,
            model=model,
            status=BatchRunStatus.PENDING.value,
        )
        self.session.add(batch_run)
        await self.session.flush()
        await self.session.refresh(batch_run)
        return batch_run

    async def get_batch_run(self, batch_run_id: UUID) -> BatchRun | None:
        """
        Get a batch run by ID.

        Args:
            batch_run_id: The batch run UUID.

        Returns:
            BatchRun or None if not found.
        """
        stmt = select(BatchRun).where(BatchRun.id == batch_run_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_batch_run_with_iterations(
        self,
        batch_run_id: UUID,
    ) -> BatchRun | None:
        """
        Get a batch run with all iterations loaded.

        Args:
            batch_run_id: The batch run UUID.

        Returns:
            BatchRun with iterations, or None if not found.
        """
        stmt = (
            select(BatchRun)
            .where(BatchRun.id == batch_run_id)
            .options(selectinload(BatchRun.iterations))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_batch_status(
        self,
        batch_run_id: UUID,
        status: BatchRunStatus,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_ms: float | None = None,
        error_message: str | None = None,
    ) -> None:
        """
        Update the status and timing of a batch run.

        Args:
            batch_run_id: The batch run UUID.
            status: New status value.
            started_at: Execution start time.
            completed_at: Execution completion time.
            duration_ms: Total duration in milliseconds.
            error_message: Error message if failed.
        """
        values: dict[str, Any] = {"status": status.value}

        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if duration_ms is not None:
            values["duration_ms"] = duration_ms
        if error_message is not None:
            values["error_message"] = error_message

        stmt = update(BatchRun).where(BatchRun.id == batch_run_id).values(**values)
        await self.session.execute(stmt)

    async def update_batch_metrics(
        self,
        batch_run_id: UUID,
        metrics: dict[str, Any],
        total_iterations: int,
        successful_iterations: int,
        failed_iterations: int,
        total_tokens: int,
    ) -> None:
        """
        Update the computed metrics for a batch run.

        Innovation: Storing pre-computed metrics enables fast dashboard queries
        without re-processing iteration data.

        Args:
            batch_run_id: The batch run UUID.
            metrics: Computed analytics dictionary.
            total_iterations: Total iteration count.
            successful_iterations: Successful iteration count.
            failed_iterations: Failed iteration count.
            total_tokens: Total tokens used.
        """
        stmt = (
            update(BatchRun)
            .where(BatchRun.id == batch_run_id)
            .values(
                metrics=metrics,
                total_iterations=total_iterations,
                successful_iterations=successful_iterations,
                failed_iterations=failed_iterations,
                total_tokens=total_tokens,
            )
        )
        await self.session.execute(stmt)


class IterationRepository:
    """
    Repository for Iteration CRUD operations.

    Innovation: The iteration repository enables bulk operations for
    efficient storage of N iteration results from Monte Carlo simulations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    async def create_iteration(
        self,
        batch_run_id: UUID,
        iteration_index: int,
        raw_response: str | None = None,
        latency_ms: float | None = None,
        is_success: bool = False,
        status: str = "pending",
        error_message: str | None = None,
        extracted_brands: list[str] | None = None,
        citations: list[str] | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
    ) -> Iteration:
        """
        Create a single iteration record.

        Args:
            batch_run_id: Parent batch run UUID.
            iteration_index: Zero-based index within the batch.
            raw_response: Complete LLM response text.
            latency_ms: Response latency in milliseconds.
            is_success: Whether iteration succeeded.
            status: Iteration status string.
            error_message: Error details if failed.
            extracted_brands: Brands mentioned in response.
            citations: Source URLs from Perplexity.
            prompt_tokens: Prompt token count.
            completion_tokens: Completion token count.
            total_tokens: Total token count.

        Returns:
            Iteration: The created iteration instance.
        """
        iteration = Iteration(
            batch_run_id=batch_run_id,
            iteration_index=iteration_index,
            raw_response=raw_response,
            latency_ms=latency_ms,
            is_success=is_success,
            status=status,
            error_message=error_message,
            extracted_brands=extracted_brands,
            citations=citations,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
        self.session.add(iteration)
        await self.session.flush()
        return iteration

    async def bulk_create_iterations(
        self,
        iterations_data: list[dict[str, Any]],
    ) -> list[Iteration]:
        """
        Bulk create iteration records for efficiency.

        Innovation: Bulk insertion significantly improves performance when
        storing N iterations from a Monte Carlo simulation.

        Args:
            iterations_data: List of iteration data dictionaries.

        Returns:
            List of created Iteration instances.
        """
        iterations = [Iteration(**data) for data in iterations_data]
        self.session.add_all(iterations)
        await self.session.flush()
        return iterations

    async def get_iterations_for_batch(
        self,
        batch_run_id: UUID,
        success_only: bool = False,
    ) -> list[Iteration]:
        """
        Get all iterations for a batch run.

        Args:
            batch_run_id: The batch run UUID.
            success_only: If True, only return successful iterations.

        Returns:
            List of iterations.
        """
        stmt = (
            select(Iteration)
            .where(Iteration.batch_run_id == batch_run_id)
            .order_by(Iteration.iteration_index)
        )

        if success_only:
            stmt = stmt.where(Iteration.is_success.is_(True))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
