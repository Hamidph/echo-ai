"""
FastAPI dependencies for authentication and authorization.

This module provides dependency functions for protecting routes with JWT or API key authentication.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db_session as get_db
from backend.app.core.security import decode_access_token, verify_api_key
from backend.app.models.user import APIKey, User

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user_from_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get the current user from a JWT token in the Authorization header.

    Args:
        credentials: HTTP Bearer credentials from the Authorization header.
        db: Database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT token
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id: UUID | None = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Fetch the user from the database
    result = await db.execute(select(User).where(User.id == UUID(str(user_id))))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_user_from_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    Get the current user from an API key in the X-API-Key header.

    Args:
        api_key: API key from the X-API-Key header.
        db: Database session.

    Returns:
        User | None: The authenticated user, or None if no API key provided.

    Raises:
        HTTPException: If the API key is invalid.
    """
    if api_key is None:
        return None

    # Fetch all active API keys (we need to hash-compare)
    result = await db.execute(
        select(APIKey).where(APIKey.is_active == True)  # noqa: E712
    )
    api_keys = result.scalars().all()

    # Check each API key
    for key_record in api_keys:
        if verify_api_key(api_key, key_record.key):
            # Update last used timestamp
            key_record.last_used_at = datetime.now(timezone.utc)
            await db.commit()

            # Fetch the user
            result = await db.execute(select(User).where(User.id == key_record.user_id))
            user = result.scalar_one_or_none()

            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive",
                )

            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


async def get_current_user(
    jwt_user: Annotated[User | None, Depends(get_current_user_from_jwt)] = None,
    api_key_user: Annotated[User | None, Depends(get_current_user_from_api_key)] = None,
) -> User:
    """
    Get the current user from either JWT or API key.

    This dependency tries JWT first, then falls back to API key.

    Args:
        jwt_user: User from JWT token (if provided).
        api_key_user: User from API key (if provided).

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If neither authentication method succeeds.
    """
    user = jwt_user or api_key_user

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current active user.

    Args:
        current_user: The authenticated user.

    Returns:
        User: The active user.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get the current user and verify they have admin role.

    Args:
        current_user: The authenticated user.

    Returns:
        User: The admin user.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required.",
        )
    return current_user


# Add missing import
from datetime import datetime, timezone  # noqa: E402
