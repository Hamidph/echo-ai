"""
FastAPI router for experiment endpoints.

This module defines the API endpoints for creating and retrieving
visibility experiments.

Innovation: These endpoints expose the "Probabilistic Visibility Analysis"
service via a RESTful API. The async design enables high-concurrency
request handling while Celery processes experiments in the background.
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.core.database import DbSession
from backend.app.models.experiment import ExperimentStatus
from backend.app.repositories.experiment_repo import (
    ExperimentRepository,
)
from backend.app.schemas.experiment import (
    BatchRunResult,
    ExperimentDetailResponse,
    ExperimentListResponse,
    ExperimentRequest,
    ExperimentResponse,
    ExperimentStatusResponse,
    IterationDetail,
    VisibilityReport,
)
from backend.app.worker import execute_experiment_task

router = APIRouter(prefix="/experiments", tags=["Experiments"])

logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=ExperimentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create a new visibility experiment",
    description="""
    Create a new probabilistic visibility experiment.

    This endpoint:
    1. Creates an experiment record in the database
    2. Triggers a background Celery task to execute the experiment
    3. Returns immediately with the experiment ID and job ID

    The experiment runs N iterations of the prompt against the specified
    LLM provider, then analyzes the results for brand visibility metrics.

    **Innovation**: This endpoint initiates a Monte Carlo simulation for
    brand visibility analysis, enabling statistically significant insights
    that single-shot queries cannot provide.
    """,
)
async def create_experiment(
    request: ExperimentRequest,
    session: DbSession,
) -> ExperimentResponse:
    """
    Create a new visibility experiment.

    Args:
        request: Experiment configuration.
        session: Database session.

    Returns:
        ExperimentResponse with experiment ID and job ID.
    """
    logger.info(f"Creating experiment for brand '{request.target_brand}'")

    # Build configuration dictionary
    config: dict[str, Any] = {
        "iterations": request.iterations,
        "temperature": request.temperature,
        "max_concurrency": request.max_concurrency,
    }
    if request.model:
        config["model"] = request.model
    if request.system_prompt:
        config["system_prompt"] = request.system_prompt

    # Create experiment in database
    exp_repo = ExperimentRepository(session)
    experiment = await exp_repo.create_experiment(
        prompt=request.prompt,
        target_brand=request.target_brand,
        config=config,
        competitor_brands=request.competitor_brands,
        domain_whitelist=request.domain_whitelist,
    )

    # Trigger Celery task
    task = execute_experiment_task.delay(
        experiment_id=str(experiment.id),
        provider=request.provider.value,
        model=request.model,
    )

    logger.info(f"Experiment {experiment.id} created, task {task.id} queued")

    return ExperimentResponse(
        experiment_id=experiment.id,
        job_id=task.id,
        status="pending",
        message=f"Experiment queued for execution with {request.iterations} iterations",
    )


@router.get(
    "/{experiment_id}",
    response_model=ExperimentStatusResponse,
    summary="Get experiment status and results",
    description="""
    Retrieve the status and results of an experiment.

    If the experiment is complete, includes computed visibility metrics.
    Poll this endpoint to check for completion.

    **Innovation**: Returns comprehensive visibility analytics including
    brand mention rates, share of voice, and consistency scores.
    """,
)
async def get_experiment(
    experiment_id: UUID,
    session: DbSession,
) -> ExperimentStatusResponse:
    """
    Get experiment status and results.

    Args:
        experiment_id: The experiment UUID.
        session: Database session.

    Returns:
        ExperimentStatusResponse with status and metrics.

    Raises:
        HTTPException: If experiment not found.
    """
    exp_repo = ExperimentRepository(session)
    experiment = await exp_repo.get_experiment_with_results(experiment_id)

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment {experiment_id} not found",
        )

    # Build batch run results
    batch_runs = [
        BatchRunResult(
            batch_run_id=br.id,
            provider=br.provider,
            model=br.model,
            status=br.status,
            started_at=br.started_at,
            completed_at=br.completed_at,
            duration_ms=br.duration_ms,
            total_iterations=br.total_iterations,
            successful_iterations=br.successful_iterations,
            failed_iterations=br.failed_iterations,
            total_tokens=br.total_tokens,
            metrics=br.metrics,
        )
        for br in experiment.batch_runs
    ]

    return ExperimentStatusResponse(
        experiment_id=experiment.id,
        prompt=experiment.prompt,
        target_brand=experiment.target_brand,
        competitor_brands=experiment.competitor_brands,
        status=experiment.status,
        error_message=experiment.error_message,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
        batch_runs=batch_runs,
    )


@router.get(
    "/{experiment_id}/detail",
    response_model=ExperimentDetailResponse,
    summary="Get detailed experiment results with iterations",
    description="""
    Retrieve detailed experiment results including individual iteration data.

    Use this endpoint for debugging or detailed analysis of response variance.
    """,
)
async def get_experiment_detail(
    experiment_id: UUID,
    session: DbSession,
) -> ExperimentDetailResponse:
    """
    Get detailed experiment results with iterations.

    Args:
        experiment_id: The experiment UUID.
        session: Database session.

    Returns:
        ExperimentDetailResponse with iteration details.

    Raises:
        HTTPException: If experiment not found.
    """
    exp_repo = ExperimentRepository(session)
    experiment = await exp_repo.get_experiment_with_results(experiment_id)

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment {experiment_id} not found",
        )

    # Build batch run results
    batch_runs = []
    all_iterations = []

    for br in experiment.batch_runs:
        batch_runs.append(
            BatchRunResult(
                batch_run_id=br.id,
                provider=br.provider,
                model=br.model,
                status=br.status,
                started_at=br.started_at,
                completed_at=br.completed_at,
                duration_ms=br.duration_ms,
                total_iterations=br.total_iterations,
                successful_iterations=br.successful_iterations,
                failed_iterations=br.failed_iterations,
                total_tokens=br.total_tokens,
                metrics=br.metrics,
            )
        )

        # Add iterations
        for iteration in br.iterations:
            all_iterations.append(
                IterationDetail(
                    iteration_index=iteration.iteration_index,
                    is_success=iteration.is_success,
                    status=iteration.status,
                    latency_ms=iteration.latency_ms,
                    raw_response=iteration.raw_response,
                    error_message=iteration.error_message,
                    extracted_brands=iteration.extracted_brands,
                )
            )

    return ExperimentDetailResponse(
        experiment_id=experiment.id,
        prompt=experiment.prompt,
        target_brand=experiment.target_brand,
        competitor_brands=experiment.competitor_brands,
        status=experiment.status,
        error_message=experiment.error_message,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
        batch_runs=batch_runs,
        iterations=all_iterations,
    )


@router.get(
    "/{experiment_id}/report",
    response_model=VisibilityReport,
    summary="Get visibility report",
    description="""
    Get a business-friendly visibility report for the experiment.

    This endpoint returns high-level metrics suitable for executive dashboards.

    **Innovation**: The visibility report distills Monte Carlo simulation
    results into actionable business intelligence.
    """,
)
async def get_visibility_report(
    experiment_id: UUID,
    session: DbSession,
) -> VisibilityReport:
    """
    Get visibility report.

    Args:
        experiment_id: The experiment UUID.
        session: Database session.

    Returns:
        VisibilityReport with key metrics.

    Raises:
        HTTPException: If experiment not found or not complete.
    """
    exp_repo = ExperimentRepository(session)
    experiment = await exp_repo.get_experiment_with_results(experiment_id)

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment {experiment_id} not found",
        )

    if experiment.status != ExperimentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experiment is {experiment.status}, report only available when completed",
        )

    # Get the first (and typically only) batch run
    if not experiment.batch_runs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No batch runs found for experiment",
        )

    batch_run = experiment.batch_runs[0]
    metrics = batch_run.metrics or {}

    # Extract visibility metrics
    target_vis = metrics.get("target_visibility", {})
    consistency = metrics.get("consistency", {})
    hallucination = metrics.get("hallucination")
    sov = metrics.get("share_of_voice", [])

    # Find target brand's share of voice
    target_sov = 0.0
    for item in sov:
        if item.get("brand") == experiment.target_brand:
            target_sov = item.get("share", 0.0)
            break

    return VisibilityReport(
        experiment_id=experiment.id,
        prompt=experiment.prompt,
        target_brand=experiment.target_brand,
        provider=batch_run.provider,
        model=batch_run.model,
        visibility_rate=target_vis.get("visibility_rate", 0.0) * 100,
        share_of_voice=target_sov * 100,
        consistency_score=consistency.get("consistency_score", 0.0) * 100,
        hallucination_rate=(
            hallucination.get("hallucination_rate", 0.0) * 100 if hallucination else None
        ),
        share_of_voice_ranking=sov,
        total_iterations=batch_run.total_iterations,
        successful_iterations=batch_run.successful_iterations,
        total_tokens=batch_run.total_tokens,
        duration_ms=batch_run.duration_ms,
        completed_at=batch_run.completed_at,
    )


@router.get(
    "",
    response_model=ExperimentListResponse,
    summary="List experiments",
    description="List experiments with pagination and optional status filter.",
)
async def list_experiments(
    session: DbSession,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status (pending, running, completed, failed)",
    ),
) -> ExperimentListResponse:
    """
    List experiments with pagination.

    Args:
        session: Database session.
        limit: Maximum results per page.
        offset: Number of results to skip.
        status_filter: Optional status filter.

    Returns:
        ExperimentListResponse with paginated results.
    """
    exp_repo = ExperimentRepository(session)

    # Parse status filter
    status_enum = None
    if status_filter:
        try:
            status_enum = ExperimentStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}",
            )

    experiments = await exp_repo.list_experiments(
        limit=limit,
        offset=offset,
        status=status_enum,
    )

    # Convert to response models
    items = [
        ExperimentStatusResponse(
            experiment_id=exp.id,
            prompt=exp.prompt,
            target_brand=exp.target_brand,
            competitor_brands=exp.competitor_brands,
            status=exp.status,
            error_message=exp.error_message,
            created_at=exp.created_at,
            updated_at=exp.updated_at,
            batch_runs=[],  # Don't include batch runs in list view
        )
        for exp in experiments
    ]

    return ExperimentListResponse(
        experiments=items,
        total=len(items),  # Would need count query for accurate total
        limit=limit,
        offset=offset,
    )
