from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class ShareOfVoiceItem(BaseModel):
    """Share of voice for a specific brand."""
    brand: str
    percentage: float = Field(..., description="Percentage share (0-100)")


class DailyVisibility(BaseModel):
    """Daily visibility metric."""
    date: date
    visibility_score: float = Field(..., description="Average visibility score (0-100)")


class DashboardStatsResponse(BaseModel):
    """Aggregated dashboard statistics."""
    
    total_experiments: int
    completed_experiments: int
    avg_visibility_score: float = Field(..., description="Weighted average visibility across all experiments")
    
    # Aggregated Share of Voice
    share_of_voice: list[ShareOfVoiceItem]
    
    # Trends
    visibility_trend: list[DailyVisibility]
