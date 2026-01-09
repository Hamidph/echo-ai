"""
Pydantic schemas for admin panel endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SystemConfigResponse(BaseModel):
    """System configuration response."""
    
    default_iterations: int = Field(..., description="Default number of iterations for new experiments")
    default_frequency: str = Field(..., description="Default frequency for recurring experiments (daily/weekly/monthly)")
    default_recurring: bool = Field(..., description="Whether recurring is enabled by default")
    max_iterations_per_experiment: int = Field(..., description="Maximum allowed iterations per experiment")
    enable_recurring_experiments: bool = Field(..., description="Whether recurring experiments are enabled platform-wide")
    maintenance_mode: bool = Field(..., description="Whether the platform is in maintenance mode")


class SystemConfigUpdate(BaseModel):
    """System configuration update request."""
    
    default_iterations: int | None = Field(None, ge=1, le=100, description="Default number of iterations")
    default_frequency: str | None = Field(None, pattern="^(daily|weekly|monthly)$", description="Default frequency")
    default_recurring: bool | None = Field(None, description="Default recurring setting")
    max_iterations_per_experiment: int | None = Field(None, ge=1, le=1000, description="Max iterations allowed")
    enable_recurring_experiments: bool | None = Field(None, description="Enable/disable recurring experiments")
    maintenance_mode: bool | None = Field(None, description="Enable/disable maintenance mode")


class AdminStatsResponse(BaseModel):
    """Platform-wide statistics for admin dashboard."""
    
    total_users: int = Field(..., description="Total number of registered users")
    active_users: int = Field(..., description="Number of active users")
    total_experiments: int = Field(..., description="Total number of experiments")
    completed_experiments: int = Field(..., description="Number of completed experiments")
    running_experiments: int = Field(..., description="Number of currently running experiments")
    recurring_experiments: int = Field(..., description="Total number of recurring experiments")
    active_recurring_experiments: int = Field(..., description="Number of active recurring experiments")
    system_config: dict[str, Any] = Field(..., description="Current system configuration")


class UserManagementResponse(BaseModel):
    """User information for admin management."""
    
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    full_name: str | None = Field(None, description="User full name")
    role: str = Field(..., description="User role (admin/user/viewer)")
    pricing_tier: str = Field(..., description="User pricing tier")
    monthly_prompt_quota: int = Field(..., description="Monthly prompt quota")
    prompts_used_this_month: int = Field(..., description="Prompts used this month")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    created_at: datetime = Field(..., description="Account creation date")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True
