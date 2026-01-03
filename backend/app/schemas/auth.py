"""
Pydantic schemas for authentication and user management.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# User registration and login
class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str | None = None


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Schema for JWT token response.

    Includes both access token (short-lived, 15 min) and refresh token (long-lived, 7 days).
    """

    access_token: str
    refresh_token: str | None = Field(None, description="Refresh token for obtaining new access tokens")
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload."""

    user_id: UUID
    email: str


# User responses
class UserResponse(BaseModel):
    """Schema for user information response."""

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    role: str
    pricing_tier: str
    monthly_prompt_quota: int
    prompts_used_this_month: int
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


# API Key management
class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(..., min_length=1, max_length=255, description="Name for this API key")


class APIKeyResponse(BaseModel):
    """Schema for API key response (includes the raw key only once)."""

    id: UUID
    name: str
    prefix: str
    key: str | None = Field(
        None, description="Full API key (only returned on creation, store it safely!)"
    )
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class APIKeyList(BaseModel):
    """Schema for listing API keys (without revealing the full key)."""

    id: UUID
    name: str
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}
