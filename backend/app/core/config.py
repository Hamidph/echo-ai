"""
Application configuration using Pydantic V2 BaseSettings.

This module provides centralized configuration management for the platform,
loading settings from environment variables and .env files with strict typing.

Innovation: Configuration supports probabilistic engine parameters like
default iteration counts and confidence interval thresholds.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, PostgresDsn, RedisDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with strict typing and environment variable support.

    All settings can be overridden via environment variables or .env file.
    Supports Docker Compose environment variable interpolation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(
        default="Echo AI - AI Search Analytics Platform",
        description="Application display name",
    )
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API version 1 prefix")

    # Security
    secret_key: str = Field(
        default="dev-secret-key-DO-NOT-USE-IN-PRODUCTION",
        description="Secret key for JWT token signing (MUST be set in production via SECRET_KEY env var)",
    )
    sentry_dsn: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking (production only)",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info: Any) -> str:
        """
        Validate that secret key is not the default in production.

        Raises:
            ValueError: If using default secret key in production environment.
        """
        environment = info.data.get("environment", "development")
        if environment == "production":
            if v == "dev-secret-key-DO-NOT-USE-IN-PRODUCTION":
                raise ValueError(
                    "SECRET_KEY must be set in production environment. "
                    "Generate a secure key with: openssl rand -hex 32"
                )
            if len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters long in production. "
                    "Generate a secure key with: openssl rand -hex 32"
                )
        return v

    # Stripe Billing
    stripe_api_key: str | None = Field(
        default=None,
        description="Stripe API key for payment processing",
    )
    stripe_webhook_secret: str | None = Field(
        default=None,
        description="Stripe webhook signing secret",
    )

    # Stripe Price IDs (overridable via environment variables)
    stripe_price_id_starter: str | None = Field(default=None, description="Stripe Price ID for Starter Tier")
    stripe_price_id_pro: str | None = Field(default=None, description="Stripe Price ID for Pro Tier")
    stripe_price_id_enterprise: str | None = Field(default=None, description="Stripe Price ID for Enterprise Tier")

    # Email Configuration
    smtp_host: str = Field(
        default="smtp.gmail.com",
        description="SMTP server host",
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP server port",
    )
    smtp_username: str | None = Field(
        default=None,
        description="SMTP username",
    )
    smtp_password: str | None = Field(
        default=None,
        description="SMTP password",
    )
    from_email: str = Field(
        default="noreply@ai-visibility.com",
        description="From email address",
    )
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for email links",
    )

    # PostgreSQL Configuration
    postgres_user: str = Field(default="ai_visibility", description="PostgreSQL username")
    postgres_password: str = Field(
        default="ai_visibility_secret",
        description="PostgreSQL password",
    )
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="ai_visibility_db", description="PostgreSQL database name")
    
    # Allow raw DATABASE_URL from environment (e.g. Railway)
    # This must be distinct from the computed properties
    raw_database_url: str | None = Field(default=None, alias="DATABASE_URL")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> PostgresDsn:
        """
        Construct PostgreSQL connection URL.
        
        Priority:
        1. DATABASE_URL env var (adjusted for asyncpg)
        2. Computed from components
        """
        if self.raw_database_url:
            url_str = self.raw_database_url
            # Ensure it uses asyncpg driver
            if url_str.startswith("postgres://"):
                url_str = url_str.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url_str.startswith("postgresql://"):
                url_str = url_str.replace("postgresql://", "postgresql+asyncpg://", 1)
            return PostgresDsn(url_str)

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> PostgresDsn:
        """
        Construct synchronous PostgreSQL connection URL for Alembic migrations.
        
        Priority:
        1. DATABASE_URL env var (adjusted for psycopg2)
        2. Computed from components
        """
        if self.raw_database_url:
            url_str = self.raw_database_url
            # Ensure it uses standard postgresql scheme (defaults to psycopg2 usually)
            # Railway often validates using postgres:// or postgresql://
            if url_str.startswith("postgres://"):
                url_str = url_str.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url_str.startswith("postgresql://"):
                # Explicitly set driver to match expectations or leave as default
                # But to be safe vs asyncpg, we make it explicit
                url_str = url_str.replace("postgresql://", "postgresql+psycopg2://", 1)
            return PostgresDsn(url_str)

        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: str = Field(default="redis_secret", description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")
    
    # Allow raw REDIS_URL from environment (e.g. Railway)
    raw_redis_url: str | None = Field(default=None, alias="REDIS_URL")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> RedisDsn:
        """
        Construct Redis connection URL.
        
        Priority:
        1. REDIS_URL env var (Railway provides this)
        2. Computed from components
        """
        if self.raw_redis_url:
            return RedisDsn(self.raw_redis_url)
            
        return RedisDsn.build(
            scheme="redis",
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            path=str(self.redis_db),
        )

    # Probabilistic Engine Configuration
    # Innovation: These parameters control the Monte Carlo simulation behavior
    default_iterations: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Default number of iterations for probabilistic queries",
    )
    max_iterations: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum allowed iterations per experiment",
    )
    confidence_level: float = Field(
        default=0.95,
        ge=0.80,
        le=0.99,
        description="Confidence level for statistical intervals",
    )

    # Testing Mode Configuration
    testing_mode: bool = Field(
        default=False,
        description="Enable testing mode with unlimited prompts",
    )
    unlimited_prompts: bool = Field(
        default=False,
        description="Disable prompt quota limits (for testing only)",
    )

    # Data Retention Policy (GDPR Compliance)
    data_retention_days: int = Field(
        default=30,
        description="Number of days to retain raw PII data (e.g. LLM responses)",
    )

    # LLM Provider API Keys (loaded from environment)
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_default_model: str = Field(
        default="gpt-4o",
        description="Default OpenAI model to use (gpt-4o matches ChatGPT UI)",
    )
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    perplexity_api_key: str | None = Field(default=None, description="Perplexity API key")

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per minute per provider",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window in seconds",
    )

    # Celery Configuration
    celery_broker_url: str | None = Field(
        default=None,
        description="Celery broker URL (defaults to Redis URL if not set)",
    )
    celery_result_backend: str | None = Field(
        default=None,
        description="Celery result backend URL (defaults to Redis URL if not set)",
    )
    celery_concurrency: int = Field(
        default=4,
        description="Number of worker processes (default 4)",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL, defaulting to Redis URL."""
        return self.celery_broker_url or str(self.redis_url)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_backend(self) -> str:
        """Get Celery result backend URL, defaulting to Redis URL."""
        return self.celery_result_backend or str(self.redis_url)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    Uses LRU cache to ensure settings are only loaded once per process.
    This is the recommended way to access settings throughout the application.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()
