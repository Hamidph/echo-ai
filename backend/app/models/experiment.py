"""
SQLAlchemy models for experiments and probabilistic batch runs.

This module defines the database schema for storing visibility experiments,
batch runs, and individual iteration results for statistical analysis.

Innovation: The three-tier model structure (Experiment → BatchRun → Iteration)
enables audit-grade data retention. Each Iteration stores raw variance data,
allowing post-hoc statistical analysis and regulatory compliance verification.
This granular storage is essential for the "Generative Risk Analytics" offering.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class ExperimentStatus(str, Enum):
    """Status of an experiment."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchRunStatus(str, Enum):
    """Status of a batch run within an experiment."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Experiment(Base):
    """
    Represents a visibility analysis experiment.

    An experiment defines the parameters for analyzing brand visibility
    across LLM providers. It contains one or more BatchRuns, each targeting
    a specific provider.

    Innovation: The Experiment model captures the full context of a visibility
    study, including target brands and configuration. This enables reproducible
    research and A/B testing of different prompt strategies.

    Attributes:
        id: Unique identifier for the experiment.
        prompt: The user prompt to analyze (e.g., "Best CRM for startups").
        target_brand: Primary brand to track visibility for.
        competitor_brands: List of competitor brands to compare against.
        config: JSON configuration (iterations, temperature, etc.).
        status: Current status of the experiment.
        created_at: When the experiment was created.
        updated_at: When the experiment was last updated.
        batch_runs: Related batch runs for this experiment.
    """

    __tablename__ = "experiments"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who created this experiment",
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="The prompt to run N times for visibility analysis",
    )
    target_brand: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Primary brand to track visibility for",
    )
    competitor_brands: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of competitor brands for Share of Voice analysis",
    )
    domain_whitelist: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Allowed domains for hallucination detection",
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Experiment configuration (iterations, temperature, etc.)",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ExperimentStatus.PENDING.value,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if experiment failed",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="experiments",
        lazy="select",  # Load on demand to prevent unnecessary joins
    )
    batch_runs: Mapped[list["BatchRun"]] = relationship(
        "BatchRun",
        back_populates="experiment",
        cascade="all, delete-orphan",
        lazy="selectin",  # Keep selectin for batch_runs as they're frequently accessed together
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_experiments_created_at", "created_at"),
        Index("ix_experiments_status_created", "status", "created_at"),
        Index("ix_experiments_user_id", "user_id"),
        Index("ix_experiments_user_status", "user_id", "status"),
        Index("ix_experiments_user_created", "user_id", "created_at"),
    )


class BatchRun(Base):
    """
    Represents a single batch run against an LLM provider.

    A BatchRun executes N iterations of the same prompt against a specific
    provider (e.g., OpenAI, Perplexity) and stores aggregated metrics.

    Innovation: The BatchRun model links experiment configuration to execution
    results, enabling cross-provider comparison. The metrics JSON field stores
    computed analytics (visibility rate, consistency score) for quick retrieval.

    Attributes:
        id: Unique identifier for the batch run.
        experiment_id: Foreign key to parent experiment.
        provider: LLM provider used (openai, anthropic, perplexity).
        model: Specific model used.
        status: Current status of the batch run.
        started_at: When execution started.
        completed_at: When execution completed.
        metrics: Computed analytics (visibility rate, consistency, etc.).
        experiment: Parent experiment relationship.
        iterations: Child iteration records.
    """

    __tablename__ = "batch_runs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    experiment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="LLM provider (openai, anthropic, perplexity)",
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Specific model used (e.g., gpt-4o, sonar)",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=BatchRunStatus.PENDING.value,
        index=True,
    )

    # Execution timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Total execution time in milliseconds",
    )

    # Aggregated metrics
    # Innovation: Pre-computed metrics enable fast dashboard queries
    # without re-processing raw iteration data
    metrics: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Computed analytics: visibility_rate, consistency_score, etc.",
    )

    # Iteration statistics
    total_iterations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    successful_iterations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    failed_iterations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Token usage
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    experiment: Mapped["Experiment"] = relationship(
        "Experiment",
        back_populates="batch_runs",
    )
    iterations: Mapped[list["Iteration"]] = relationship(
        "Iteration",
        back_populates="batch_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (Index("ix_batch_runs_experiment_provider", "experiment_id", "provider"),)


class Iteration(Base):
    """
    Stores individual iteration data from a batch run.

    Each Iteration represents a single LLM API call within a Monte Carlo
    simulation. Raw response data is preserved for audit and re-analysis.

    Innovation: The Iteration model stores raw variance data for audit purposes.
    This granular storage enables:
    1. Post-hoc statistical analysis with different algorithms
    2. Regulatory compliance (full audit trail of AI recommendations)
    3. Hallucination detection by comparing responses across iterations
    4. Research into LLM response consistency and reliability

    The raw_response field preserves the complete LLM output, while
    extracted_brands enables efficient querying without full-text search.

    Attributes:
        id: Unique identifier for the iteration.
        batch_run_id: Foreign key to parent batch run.
        iteration_index: Zero-based index within the batch.
        raw_response: Complete text response from the LLM.
        latency_ms: Response time in milliseconds.
        is_success: Whether the iteration completed successfully.
        error_message: Error details if iteration failed.
        extracted_brands: Brands mentioned in the response (for quick queries).
        citations: Source URLs if provider supports citations (Perplexity).
        batch_run: Parent batch run relationship.
    """

    __tablename__ = "iterations"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    batch_run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("batch_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    iteration_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Zero-based index within the batch",
    )

    # Response data
    # Innovation: Raw response storage enables variance analysis and audit trails
    raw_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Complete LLM response text for variance analysis",
    )
    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Response latency in milliseconds",
    )
    is_success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Iteration status: success, failed, rate_limited, timeout",
    )

    # Extracted data for efficient querying
    # Innovation: Pre-extracted brands enable fast visibility queries
    # without expensive full-text search on raw_response
    extracted_brands: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Brands mentioned in this response",
    )
    citations: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Source URLs from Perplexity responses",
    )

    # Token usage for this iteration
    prompt_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    completion_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    batch_run: Mapped["BatchRun"] = relationship(
        "BatchRun",
        back_populates="iterations",
    )

    __table_args__ = (
        Index("ix_iterations_batch_success", "batch_run_id", "is_success"),
        Index("ix_iterations_batch_index", "batch_run_id", "iteration_index"),
        Index("ix_iterations_status", "status"),  # For filtering by status
    )
