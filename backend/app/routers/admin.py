"""
Admin panel API endpoints for system configuration and management.

This module provides admin-only endpoints for:
- System configuration (default settings)
- User management
- Experiment defaults
- Platform statistics
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db_session as get_db
from backend.app.core.deps import get_current_admin_user
from backend.app.models.experiment import Experiment, ExperimentStatus
from backend.app.models.user import User, UserRole
from backend.app.schemas.admin import (
    AdminStatsResponse,
    SystemConfigResponse,
    SystemConfigUpdate,
    UserManagementResponse,
)

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


# In-memory system configuration (in production, use Redis or database)
_system_config = {
    "default_iterations": 10,
    "default_frequency": "daily",  # daily, weekly, monthly
    "default_recurring": False,
    "max_iterations_per_experiment": 100,
    "enable_recurring_experiments": True,
    "maintenance_mode": False,
}


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config(
    current_admin: Annotated[User, Depends(get_current_admin_user)],
) -> dict[str, Any]:
    """
    Get current system configuration.
    
    **Admin only**: Requires admin role.
    
    Returns:
        System configuration including default settings for experiments.
    """
    logger.info(f"Admin {current_admin.email} retrieved system config")
    return _system_config


@router.put("/config", response_model=SystemConfigResponse)
async def update_system_config(
    config_update: SystemConfigUpdate,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
) -> dict[str, Any]:
    """
    Update system configuration.
    
    **Admin only**: Requires admin role.
    
    This endpoint allows admins to change default settings for the platform,
    including default iteration counts, recurring experiment frequency, etc.
    
    Args:
        config_update: Configuration updates to apply.
        current_admin: Authenticated admin user.
    
    Returns:
        Updated system configuration.
    """
    logger.info(f"Admin {current_admin.email} updating system config: {config_update.model_dump(exclude_unset=True)}")
    
    # Update only provided fields
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in _system_config:
            _system_config[key] = value
    
    logger.info(f"System config updated successfully")
    return _system_config


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get platform-wide statistics.
    
    **Admin only**: Requires admin role.
    
    Returns comprehensive statistics about the platform including:
    - Total users, experiments, iterations
    - Active recurring experiments
    - Resource usage
    
    Args:
        current_admin: Authenticated admin user.
        session: Database session.
    
    Returns:
        Platform statistics.
    """
    logger.info(f"Admin {current_admin.email} retrieving platform stats")
    
    # Get user counts
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    active_users_result = await session.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0
    
    # Get experiment counts
    total_experiments_result = await session.execute(select(func.count(Experiment.id)))
    total_experiments = total_experiments_result.scalar() or 0
    
    completed_experiments_result = await session.execute(
        select(func.count(Experiment.id)).where(Experiment.status == ExperimentStatus.COMPLETED.value)
    )
    completed_experiments = completed_experiments_result.scalar() or 0
    
    running_experiments_result = await session.execute(
        select(func.count(Experiment.id)).where(Experiment.status == ExperimentStatus.RUNNING.value)
    )
    running_experiments = running_experiments_result.scalar() or 0
    
    # Get recurring experiment counts
    recurring_experiments_result = await session.execute(
        select(func.count(Experiment.id)).where(Experiment.is_recurring == True)
    )
    recurring_experiments = recurring_experiments_result.scalar() or 0
    
    active_recurring_result = await session.execute(
        select(func.count(Experiment.id)).where(
            Experiment.is_recurring == True,
            Experiment.status != ExperimentStatus.FAILED.value,
            Experiment.status != ExperimentStatus.CANCELLED.value,
        )
    )
    active_recurring = active_recurring_result.scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_experiments": total_experiments,
        "completed_experiments": completed_experiments,
        "running_experiments": running_experiments,
        "recurring_experiments": recurring_experiments,
        "active_recurring_experiments": active_recurring,
        "system_config": _system_config,
    }


@router.get("/users", response_model=list[UserManagementResponse])
async def list_users(
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> list[User]:
    """
    List all users with pagination.
    
    **Admin only**: Requires admin role.
    
    Args:
        current_admin: Authenticated admin user.
        session: Database session.
        limit: Maximum number of users to return.
        offset: Number of users to skip.
    
    Returns:
        List of users with their details.
    """
    logger.info(f"Admin {current_admin.email} listing users (limit={limit}, offset={offset})")
    
    result = await session.execute(
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()
    
    return list(users)


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Update a user's role.
    
    **Admin only**: Requires admin role.
    
    Args:
        user_id: UUID of the user to update.
        new_role: New role to assign.
        current_admin: Authenticated admin user.
        session: Database session.
    
    Returns:
        Success message.
    """
    logger.info(f"Admin {current_admin.email} updating user {user_id} role to {new_role}")
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent admin from demoting themselves
    if str(user.id) == str(current_admin.id) and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role",
        )
    
    user.role = new_role.value
    await session.commit()
    
    logger.info(f"User {user_id} role updated to {new_role}")
    return {"message": f"User role updated to {new_role}"}


@router.patch("/users/{user_id}/quota")
async def update_user_quota(
    user_id: str,
    new_quota: int,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Update a user's monthly prompt quota.
    
    **Admin only**: Requires admin role.
    
    Args:
        user_id: UUID of the user to update.
        new_quota: New monthly prompt quota.
        current_admin: Authenticated admin user.
        session: Database session.
    
    Returns:
        Success message.
    """
    logger.info(f"Admin {current_admin.email} updating user {user_id} quota to {new_quota}")
    
    if new_quota < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quota cannot be negative",
        )
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.monthly_prompt_quota = new_quota
    await session.commit()
    
    logger.info(f"User {user_id} quota updated to {new_quota}")
    return {"message": f"User quota updated to {new_quota}"}
