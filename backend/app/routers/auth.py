"""
Authentication and user management endpoints.

This module provides routes for user registration, login, and API key management.
"""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db_session as get_db
from backend.app.core.deps import get_current_active_user
from backend.app.core.security import (
    create_access_token,
    generate_api_key,
    get_api_key_prefix,
    get_password_hash,
    verify_password,
)
from backend.app.models.user import APIKey, PricingTier, User, UserRole
from backend.app.schemas.auth import (
    APIKeyCreate,
    APIKeyList,
    APIKeyResponse,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Register a new user account.

    Creates a new user with the FREE pricing tier and default quota.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.USER.value,
        pricing_tier=PricingTier.FREE.value,
        monthly_iteration_quota=100,  # Free tier quota
        quota_reset_date=datetime.utcnow() + timedelta(days=30),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send verification email
    from backend.app.services.email import send_verification_email
    try:
        await send_verification_email(
            user_email=new_user.email,
            user_name=new_user.full_name or new_user.email,
            user_id=str(new_user.id),
        )
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {e}")

    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Login with email and password.

    Returns a JWT access token for API authentication.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token = create_access_token(data={"user_id": str(user.id), "email": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current user information.

    Requires authentication via JWT or API key.
    """
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> APIKeyResponse:
    """
    Create a new API key for programmatic access.

    The full API key is only returned once. Store it securely!
    """
    # Generate API key
    raw_key, hashed_key = generate_api_key()
    prefix = get_api_key_prefix(raw_key)

    # Create API key record
    api_key = APIKey(
        user_id=current_user.id,
        key=hashed_key,
        prefix=prefix,
        name=api_key_data.name,
    )

    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Return response with the raw key (only time it's shown)
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        prefix=api_key.prefix,
        key=raw_key,  # Only returned on creation!
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
    )


@router.get("/api-keys", response_model=list[APIKeyList])
async def list_api_keys(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[APIKey]:
    """
    List all API keys for the current user.

    Does not return the full API key values.
    """
    result = await db.execute(select(APIKey).where(APIKey.user_id == current_user.id))
    api_keys = result.scalars().all()
    return list(api_keys)


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Revoke (delete) an API key.

    Only the owner of the API key can revoke it.
    """
    result = await db.execute(
        select(APIKey).where(APIKey.id == api_key_id, APIKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    # Soft delete by setting revoked_at and deactivating
    api_key.is_active = False
    api_key.revoked_at = datetime.utcnow()
    await db.commit()


@router.post("/verify-email/{token}", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Verify user email address using token from email.
    """
    from backend.app.core.security import decode_access_token

    # Decode token
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )

    # Get user and mark as verified
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    await db.commit()

    # Send welcome email
    from backend.app.services.email import send_welcome_email
    try:
        await send_welcome_email(
            user_email=user.email,
            user_name=user.full_name or user.email,
        )
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

    return {"message": "Email verified successfully"}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Resend verification email to current user.
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    from backend.app.services.email import send_verification_email
    try:
        await send_verification_email(
            user_email=current_user.email,
            user_name=current_user.full_name or current_user.email,
            user_id=str(current_user.id),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {e!s}",
        )

    return {"message": "Verification email sent"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Request password reset email.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a password reset link has been sent"}

    from backend.app.services.email import send_password_reset_email
    try:
        await send_password_reset_email(
            user_email=user.email,
            user_name=user.full_name or user.email,
            user_id=str(user.id),
        )
    except Exception as e:
        print(f"Failed to send password reset email: {e}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password/{token}", status_code=status.HTTP_200_OK)
async def reset_password(
    token: str,
    new_password: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Reset password using token from email.
    """
    from backend.app.core.security import decode_access_token

    # Decode token
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )

    # Get user and update password
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password
    user.hashed_password = get_password_hash(new_password)
    await db.commit()

    return {"message": "Password reset successfully"}
