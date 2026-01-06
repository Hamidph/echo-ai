"""
FastAPI router for experiment endpoints.

This module defines the API endpoints for creating and retrieving
visibility experiments.

Innovation: These endpoints expose the "Probabilistic Visibility Analysis"
service via a RESTful API. The async design enables high-concurrency
request handling while Celery processes experiments in the background.
"""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.core.config import get_settings
from backend.app.core.database import DbSession
from backend.app.core.deps import get_current_active_user
from backend.app.models.user import User
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
limiter = Limiter(key_func=get_remote_address)


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

    **Rate Limit**: 10 requests per minute per user
    """,
)
@limiter.limit("10/minute")
async def create_experiment(
    experiment_request: ExperimentRequest,
    request: Request,
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ExperimentResponse:
    """
    Create a new visibility experiment.

    Args:
        experiment_request: Experiment configuration.
        session: Database session.
        current_user: Authenticated user creating the experiment.

    Returns:
        ExperimentResponse with experiment ID and job ID.
    """
    logger.info(
        f"User {current_user.email} creating experiment for brand '{experiment_request.target_brand}'"
    )

    # Validate iterations against max allowed BEFORE quota check
    settings = get_settings()
    iterations_requested = experiment_request.iterations
    if iterations_requested > settings.max_iterations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Iterations ({iterations_requested}) exceeds maximum allowed ({settings.max_iterations})",
        )

    # Check quota (skip if testing mode is enabled)
    # IMPORTANT: Quota is based on number of prompts (iterations), not experiments
    if not settings.testing_mode and not settings.unlimited_prompts:
        prompts_needed = iterations_requested
        if current_user.prompts_used_this_month + prompts_needed > current_user.monthly_prompt_quota:
            remaining = current_user.monthly_prompt_quota - current_user.prompts_used_this_month
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient quota. Need {prompts_needed} prompts, have {remaining} remaining. Used: {current_user.prompts_used_this_month}/{current_user.monthly_prompt_quota}",
            )

        # Increment usage counter by number of iterations
        current_user.prompts_used_this_month += prompts_needed
        await session.commit()
        await session.refresh(current_user)
        logger.info(f"User {current_user.email} quota: {current_user.prompts_used_this_month}/{current_user.monthly_prompt_quota} (used {prompts_needed} prompts)")
    else:
        logger.info(f"Testing mode enabled - skipping quota check for user {current_user.email}")

    # Build configuration dictionary
    config: dict[str, Any] = {
        "iterations": experiment_request.iterations,
        "temperature": experiment_request.temperature,
        "max_concurrency": experiment_request.max_concurrency,
    }
    if experiment_request.model:
        config["model"] = experiment_request.model
    if experiment_request.system_prompt:
        config["system_prompt"] = experiment_request.system_prompt

    # Create experiment in database
    exp_repo = ExperimentRepository(session)
    experiment = await exp_repo.create_experiment(
        user_id=current_user.id,
        prompt=experiment_request.prompt,
        target_brand=experiment_request.target_brand,
        config=config,
        competitor_brands=experiment_request.competitor_brands,
        domain_whitelist=experiment_request.domain_whitelist,
    )

    # Trigger Celery task
    try:
        task = execute_experiment_task.delay(
            experiment_id=str(experiment.id),
            provider=experiment_request.provider.value,
            model=experiment_request.model,
        )
    except Exception as e:
        logger.error(f"Failed to queue experiment task: {e}")
        # Refund quota
        if not settings.testing_mode and not settings.unlimited_prompts:
            current_user.prompts_used_this_month -= iterations_requested
            await session.commit()
            logger.info(f"Refunded {iterations_requested} prompts to user {current_user.email} due to queue failure")
        
        # Mark as failed
        await exp_repo.update_experiment_status(
             experiment.id,
             ExperimentStatus.FAILED,
             error_message="System overloaded, please try again later."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to queue experiment. Quota has been refunded.",
        )

    logger.info(f"Experiment {experiment.id} created, task {task.id} queued")

    return ExperimentResponse(
        experiment_id=experiment.id,
        job_id=task.id,
        status="pending",
        message=f"Experiment queued for execution with {experiment_request.iterations} iterations",
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
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ExperimentStatusResponse:
    """
    Get experiment status and results.

    Args:
        experiment_id: The experiment UUID.
        session: Database session.
        current_user: Authenticated user requesting the experiment.

    Returns:
        ExperimentStatusResponse with status and metrics.

    Raises:
        HTTPException: If experiment not found.
    """
    exp_repo = ExperimentRepository(session)
    # Verify ownership before fetching results
    experiment = await exp_repo.get_experiment_by_user(experiment_id, current_user.id)

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found or access denied",
        )

    # Now load full results (which might already be loaded by get_experiment_by_user if the repo method supported it, 
    # but based on line 264 we need to verify first then load full if separate).
    # actually wait, get_experiment_with_results loads relationships. 
    # Let's check if we can just stick to get_experiment_by_user check then re-fetch or if we should modify the repo. 
    # For minimally invasive fix that is secure:
    # 1. Check ownership.
    # 2. If valid, fetch with results.
    
    experiment_with_results = await exp_repo.get_experiment_with_results(experiment_id)
    if not experiment_with_results:
         # Should not happen if first check passed, but safe guard
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment found but could not load results",
        )
    experiment = experiment_with_results

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
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ExperimentDetailResponse:
    """
    Get detailed experiment results with iterations.

    Args:
        experiment_id: The experiment UUID.
        session: Database session.
        current_user: Authenticated user requesting the experiment.

    Returns:
        ExperimentDetailResponse with iteration details.

    Raises:
        HTTPException: If experiment not found or access denied.
    """
    exp_repo = ExperimentRepository(session)

    # Verify ownership before fetching results
    experiment = await exp_repo.get_experiment_by_user(experiment_id, current_user.id)

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found or access denied",
        )

    # Now load full results with iterations
    experiment = await exp_repo.get_experiment_with_results(experiment_id)

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
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> VisibilityReport:
    """
    Get visibility report.

    Args:
        experiment_id: The experiment UUID.
        session: Database session.
        current_user: Authenticated user requesting the report.

    Returns:
        VisibilityReport with key metrics.

    Raises:
        HTTPException: If experiment not found, access denied, or not complete.
    """
    exp_repo = ExperimentRepository(session)

    # Verify ownership before fetching results
    experiment = await exp_repo.get_experiment_by_user(experiment_id, current_user.id)

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found or access denied",
        )

    # Load full results
    experiment = await exp_repo.get_experiment_with_results(experiment_id)

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
    current_user: Annotated[User, Depends(get_current_active_user)],
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
        current_user: Authenticated user.
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
        user_id=current_user.id,
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
