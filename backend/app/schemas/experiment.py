"""
Pydantic schemas for experiment API requests and responses.

This module defines the API contract for creating and retrieving
visibility experiments.

Innovation: These schemas enable a clean API interface for the
"Probabilistic Visibility Analysis" service, supporting both
synchronous status checks and async webhook notifications.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.llm import LLMProvider


class ExperimentRequest(BaseModel):
    """
    Request schema for creating a new experiment.

    Innovation: This schema captures all parameters needed for a
    probabilistic visibility study, including target brand, competitors,
    and Monte Carlo configuration.
    """

    prompt: str = Field(
        min_length=10,
        max_length=10000,
        description="The prompt to analyze (e.g., 'Best CRM for startups')",
        examples=["What are the best CRM tools for small businesses?"],
    )
    target_brand: str = Field(
        min_length=1,
        max_length=255,
        description="Primary brand to track visibility for",
        examples=["Salesforce"],
    )
    competitor_brands: list[str] | None = Field(
        default=None,
        max_length=20,
        description="Optional list of competitor brands for Share of Voice analysis",
        examples=[["HubSpot", "Pipedrive", "Zoho CRM"]],
    )
    provider: LLMProvider = Field(
        description="LLM provider to use",
        examples=[LLMProvider.PERPLEXITY],
    )
    model: str | None = Field(
        default=None,
        description="Optional model override (uses provider default if not set)",
        examples=["sonar", "gpt-4o"],
    )
    iterations: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of iterations for Monte Carlo simulation",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (higher = more variance)",
    )
    max_concurrency: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum concurrent API requests",
    )
    domain_whitelist: list[str] | None = Field(
        default=None,
        description="Trusted domains for hallucination detection (Perplexity only)",
        examples=[["salesforce.com", "hubspot.com", "forbes.com"]],
    )
    system_prompt: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional system prompt for all iterations",
    )


class ExperimentResponse(BaseModel):
    """
    Response schema for experiment creation.

    Returns the experiment ID and job ID for status tracking.
    """

    experiment_id: UUID = Field(description="Unique experiment identifier")
    job_id: str = Field(description="Celery task ID for status tracking")
    status: str = Field(description="Initial status (pending)")
    message: str = Field(description="Human-readable status message")


class BatchRunResult(BaseModel):
    """
    Result schema for a single batch run.

    Contains execution stats and computed metrics.
    """

    batch_run_id: UUID = Field(description="Batch run identifier")
    provider: str = Field(description="LLM provider used")
    model: str = Field(description="Model used")
    status: str = Field(description="Batch status")
    started_at: datetime | None = Field(description="Execution start time")
    completed_at: datetime | None = Field(description="Execution completion time")
    duration_ms: float | None = Field(description="Total duration in milliseconds")
    total_iterations: int = Field(description="Total iterations attempted")
    successful_iterations: int = Field(description="Successful iterations")
    failed_iterations: int = Field(description="Failed iterations")
    total_tokens: int = Field(description="Total tokens consumed")
    metrics: dict[str, Any] | None = Field(description="Computed analytics")


class IterationDetail(BaseModel):
    """
    Detail schema for a single iteration.

    Used for detailed result inspection.
    """

    iteration_index: int = Field(description="Zero-based iteration index")
    is_success: bool = Field(description="Whether iteration succeeded")
    status: str = Field(description="Iteration status")
    latency_ms: float | None = Field(description="Response latency")
    raw_response: str | None = Field(description="LLM response text")
    error_message: str | None = Field(description="Error if failed")
    extracted_brands: list[str] | None = Field(description="Brands mentioned")


class ExperimentStatusResponse(BaseModel):
    """
    Response schema for experiment status check.

    Innovation: This comprehensive response enables clients to:
    1. Poll for completion status
    2. Access computed metrics when complete
    3. Inspect individual iterations for debugging
    """

    experiment_id: UUID = Field(description="Experiment identifier")
    prompt: str = Field(description="The analyzed prompt")
    target_brand: str = Field(description="Primary target brand")
    competitor_brands: list[str] | None = Field(description="Competitor brands")
    status: str = Field(description="Experiment status")
    error_message: str | None = Field(description="Error if failed")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    batch_runs: list[BatchRunResult] = Field(
        default_factory=list,
        description="Results from batch runs",
    )


class ExperimentDetailResponse(ExperimentStatusResponse):
    """
    Extended response with full iteration details.

    Used for detailed inspection of experiment results.
    """

    iterations: list[IterationDetail] = Field(
        default_factory=list,
        description="Individual iteration results",
    )


class ExperimentListResponse(BaseModel):
    """
    Response schema for listing experiments.
    """

    experiments: list[ExperimentStatusResponse] = Field(description="List of experiments")
    total: int = Field(description="Total count")
    limit: int = Field(description="Page size")
    offset: int = Field(description="Page offset")


class VisibilityReport(BaseModel):
    """
    High-level visibility report for business users.

    Innovation: This schema presents the "Probabilistic Visibility Analysis"
    results in a business-friendly format, suitable for executive dashboards.
    """

    experiment_id: UUID = Field(description="Experiment identifier")
    prompt: str = Field(description="Analyzed prompt")
    target_brand: str = Field(description="Target brand")
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model used")

    # Key metrics
    visibility_rate: float = Field(
        description="Percentage of responses mentioning target brand (0-100)"
    )
    share_of_voice: float = Field(description="Target brand's share of all brand mentions (0-100)")
    consistency_score: float = Field(
        description="Response consistency score (0-100, higher = more consistent)"
    )
    hallucination_rate: float | None = Field(
        default=None,
        description="Rate of unverified citations (0-100, Perplexity only)",
    )

    # Competitive analysis
    share_of_voice_ranking: list[dict[str, Any]] = Field(
        default_factory=list,
        description="All brands ranked by Share of Voice",
    )

    # Metadata
    total_iterations: int = Field(description="Number of iterations")
    successful_iterations: int = Field(description="Successful iterations")
    total_tokens: int = Field(description="Tokens consumed")
    duration_ms: float | None = Field(description="Execution time")
    completed_at: datetime | None = Field(description="Completion timestamp")
