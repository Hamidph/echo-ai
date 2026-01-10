"""Brand management schemas."""

from pydantic import BaseModel, Field


class BrandProfileBase(BaseModel):
    """Base brand profile schema."""

    brand_name: str = Field(..., min_length=1, max_length=100, description="Company/brand name")
    brand_description: str | None = Field(None, max_length=500, description="What your company does")
    brand_website: str | None = Field(None, description="Company website URL")
    brand_industry: str | None = Field(None, max_length=100, description="Industry/category")


class BrandProfileCreate(BrandProfileBase):
    """Schema for creating/updating brand profile."""

    brand_competitors: list[str] = Field(
        default_factory=list, max_length=10, description="Competitor names"
    )
    brand_target_keywords: list[str] = Field(
        default_factory=list, max_length=20, description="Target SEO keywords"
    )


class BrandProfileResponse(BrandProfileBase):
    """Schema for brand profile response."""

    brand_competitors: list[str] = Field(default_factory=list)
    brand_target_keywords: list[str] = Field(default_factory=list)
    has_brand_profile: bool = Field(..., description="Whether user has completed brand setup")

    model_config = {"from_attributes": True}


class CompetitorAdd(BaseModel):
    """Schema for adding a competitor."""

    competitor_name: str = Field(..., min_length=1, max_length=100)


class CompetitorRemove(BaseModel):
    """Schema for removing a competitor."""

    competitor_name: str = Field(..., min_length=1, max_length=100)
