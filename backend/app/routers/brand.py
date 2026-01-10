"""Brand management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.database import DbSession
from backend.app.core.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.schemas.brand import (
    BrandProfileCreate,
    BrandProfileResponse,
    CompetitorAdd,
    CompetitorRemove,
)

router = APIRouter(prefix="/brand", tags=["Brand"])


@router.get("/profile", response_model=BrandProfileResponse)
async def get_brand_profile(
    current_user: User = Depends(get_current_active_user),
) -> BrandProfileResponse:
    """Get current user's brand profile."""
    has_profile = bool(current_user.brand_name)

    return BrandProfileResponse(
        brand_name=current_user.brand_name or "",
        brand_description=current_user.brand_description,
        brand_website=current_user.brand_website,
        brand_industry=current_user.brand_industry,
        brand_competitors=current_user.brand_competitors or [],
        brand_target_keywords=current_user.brand_target_keywords or [],
        has_brand_profile=has_profile,
    )


@router.put("/profile", response_model=BrandProfileResponse)
async def update_brand_profile(
    profile: BrandProfileCreate,
    session: DbSession,
    current_user: User = Depends(get_current_active_user),
) -> BrandProfileResponse:
    """Update user's brand profile."""
    # Update brand fields
    current_user.brand_name = profile.brand_name
    current_user.brand_description = profile.brand_description
    current_user.brand_website = profile.brand_website
    current_user.brand_industry = profile.brand_industry
    current_user.brand_competitors = profile.brand_competitors
    current_user.brand_target_keywords = profile.brand_target_keywords

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return BrandProfileResponse(
        brand_name=current_user.brand_name,
        brand_description=current_user.brand_description,
        brand_website=current_user.brand_website,
        brand_industry=current_user.brand_industry,
        brand_competitors=current_user.brand_competitors or [],
        brand_target_keywords=current_user.brand_target_keywords or [],
        has_brand_profile=True,
    )


@router.post("/competitors", response_model=BrandProfileResponse)
async def add_competitor(
    competitor: CompetitorAdd,
    session: DbSession,
    current_user: User = Depends(get_current_active_user),
) -> BrandProfileResponse:
    """Add a competitor to user's brand profile."""
    competitors = list(current_user.brand_competitors or [])

    # Check if already exists
    if competitor.competitor_name in competitors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Competitor already exists",
        )

    # Check max limit
    if len(competitors) >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 competitors allowed",
        )

    competitors.append(competitor.competitor_name)
    current_user.brand_competitors = competitors

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return BrandProfileResponse(
        brand_name=current_user.brand_name or "",
        brand_description=current_user.brand_description,
        brand_website=current_user.brand_website,
        brand_industry=current_user.brand_industry,
        brand_competitors=competitors,
        brand_target_keywords=current_user.brand_target_keywords or [],
        has_brand_profile=bool(current_user.brand_name),
    )


@router.delete("/competitors", response_model=BrandProfileResponse)
async def remove_competitor(
    competitor: CompetitorRemove,
    session: DbSession,
    current_user: User = Depends(get_current_active_user),
) -> BrandProfileResponse:
    """Remove a competitor from user's brand profile."""
    competitors = list(current_user.brand_competitors or [])

    if competitor.competitor_name not in competitors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )

    competitors.remove(competitor.competitor_name)
    current_user.brand_competitors = competitors

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return BrandProfileResponse(
        brand_name=current_user.brand_name or "",
        brand_description=current_user.brand_description,
        brand_website=current_user.brand_website,
        brand_industry=current_user.brand_industry,
        brand_competitors=competitors,
        brand_target_keywords=current_user.brand_target_keywords or [],
        has_brand_profile=bool(current_user.brand_name),
    )
