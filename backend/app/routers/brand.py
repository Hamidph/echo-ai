"""Brand management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db_session as get_session
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.brand import (
    BrandProfileCreate,
    BrandProfileResponse,
    CompetitorAdd,
    CompetitorRemove,
)

router = APIRouter(tags=["brand"])


@router.get("/brand/profile", response_model=BrandProfileResponse)
async def get_brand_profile(
    current_user: User = Depends(get_current_user),
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


@router.put("/brand/profile", response_model=BrandProfileResponse)
async def update_brand_profile(
    profile: BrandProfileCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
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


@router.post("/brand/competitors", response_model=BrandProfileResponse)
async def add_competitor(
    competitor: CompetitorAdd,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BrandProfileResponse:
    """Add a competitor to user's brand profile."""
    competitors = current_user.brand_competitors or []
    
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


@router.delete("/brand/competitors", response_model=BrandProfileResponse)
async def remove_competitor(
    competitor: CompetitorRemove,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BrandProfileResponse:
    """Remove a competitor from user's brand profile."""
    competitors = current_user.brand_competitors or []
    
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
