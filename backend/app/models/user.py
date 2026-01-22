"""
User models for authentication and authorization.

This module defines the database schema for users, API keys, and usage tracking.
"""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class UserRole(str, Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class PricingTier(str, Enum):
    """Pricing tiers for billing."""

    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ENTERPRISE_PLUS = "enterprise_plus"


class User(Base):
    """
    User account model.

    Stores user credentials, profile information, and subscription details.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="User email address (unique identifier)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password",
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the user account is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the user email has been verified",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.USER.value,
        comment="User role (admin, user, viewer)",
    )

    # Pricing tier and usage limits
    pricing_tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=PricingTier.FREE.value,
        comment="Current pricing tier",
    )
    monthly_prompt_quota: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        comment="Monthly prompt quota based on pricing tier (each prompt runs 10 iterations)",
    )
    prompts_used_this_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Prompts (experiments) used in current billing period",
    )
    quota_reset_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the monthly quota resets",
    )

    # Stripe integration
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="Stripe customer ID for billing",
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Stripe subscription ID",
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
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Brand Management (Phase 1)
    brand_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Company/Brand name",
    )
    brand_description: Mapped[str | None] = mapped_column(
        String, # Text type in Postgres
        nullable=True,
        comment="Description of what the brand does",
    )
    brand_website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Company website URL",
    )
    brand_industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Industry category",
    )
    # Storing lists as JSON for simplicity in MVP (Phase 1)
    # Ideally these would be separate tables if we need complex queries later
    from sqlalchemy.dialects.postgresql import JSONB
    brand_competitors: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of competitor names",
    )
    brand_target_keywords: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of target SEO keywords",
    )
    experiments: Mapped[list["Experiment"]] = relationship(
        "Experiment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_users_pricing_tier", "pricing_tier"),
        Index("ix_users_created_at", "created_at"),
    )


class APIKey(Base):
    """
    API key model for programmatic access.

    Allows users to create multiple API keys for different applications.
    """

    __tablename__ = "api_keys"

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
    )
    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Hashed API key (bcrypt)",
    )
    prefix: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Display prefix of key (e.g., 'sk_live_abc1...')",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User-provided name for the API key",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the API key is active",
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time this API key was used",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this API key expires (optional)",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this API key was revoked",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="api_keys",
    )

    __table_args__ = (
        Index("ix_api_keys_user_active", "user_id", "is_active"),
        Index("ix_api_keys_created_at", "created_at"),
    )
