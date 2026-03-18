"""
Authentication and user management endpoints.

This module provides routes for user registration, login, and API key management.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db_session as get_db
from backend.app.core.deps import get_current_active_user
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
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

logger = logging.getLogger(__name__)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class VerifyEmailRequest(BaseModel):
    token: str


router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")  # Prevent spam registrations
async def register(
    user_data: UserRegister,
    request: Request,  # noqa: ARG001
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
        monthly_prompt_quota=3,  # Free tier quota (3 prompts/month, each runs 10 iterations)
        quota_reset_date=datetime.now(UTC) + timedelta(days=30),
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
        logger.error(f"Failed to send verification email: {e}", exc_info=True)

    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Prevent brute force attacks
async def login(
    login_data: UserLogin,
    request: Request,  # noqa: ARG001
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Login with email and password.

    Returns both access token (15 min TTL) and refresh token (7 day TTL).
    Use the refresh token to obtain new access tokens without re-authenticating.
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
    user.last_login_at = datetime.now(UTC)
    await db.commit()

    # Create access token (short-lived) and refresh token (long-lived)
    access_token = create_access_token(data={"user_id": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"user_id": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    body: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Refresh an access token using a valid refresh token.

    Implements token rotation: the old refresh token is blacklisted and a new
    token pair is issued. Reuse of a consumed refresh token triggers full
    session revocation (theft detection).
    """
    from backend.app.core.security import (
        blacklist_all_user_tokens,
        blacklist_token,
        is_token_blacklisted,
    )

    # Decode and validate refresh token
    payload = decode_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    # Check for token replay (theft detection)
    if jti and await is_token_blacklisted(jti):
        logger.warning(f"Refresh token replay detected for user {user_id}")
        await blacklist_all_user_tokens(user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token reuse detected. All sessions revoked.",
        )

    # Blacklist the consumed refresh token
    if jti:
        await blacklist_token(jti, REFRESH_TOKEN_EXPIRE_DAYS * 86400)

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Issue new token pair (rotation)
    access_token = create_access_token(data={"user_id": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token(data={"user_id": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    body: LogoutRequest | None = None,
    current_user: User = Depends(get_current_active_user),  # noqa: ARG001
) -> dict[str, str]:
    """
    Logout the current user by blacklisting their access token.

    Optionally accepts a refresh_token in the body to also blacklist it.
    """
    from backend.app.core.security import blacklist_token

    # Blacklist the access token
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        from jose import jwt as jose_jwt

        from backend.app.core.security import ALGORITHM, get_secret_key

        try:
            payload = jose_jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
            jti = payload.get("jti")
            if jti:
                # Blacklist for remaining TTL (15 min access tokens)
                await blacklist_token(jti, 900)
        except Exception:
            pass

    # Also blacklist refresh token if provided
    if body and body.refresh_token:
        try:
            payload = decode_refresh_token(body.refresh_token)
            if payload and payload.get("jti"):
                await blacklist_token(payload["jti"], REFRESH_TOKEN_EXPIRE_DAYS * 86400)
        except Exception:
            pass

    return {"message": "Logged out successfully"}


@router.post("/revoke-all-sessions", status_code=status.HTTP_200_OK)
async def revoke_all_sessions(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Revoke all active sessions for the current user.

    All existing tokens (access and refresh) issued before this point
    will be invalidated.
    """
    from backend.app.core.security import blacklist_all_user_tokens

    await blacklist_all_user_tokens(str(current_user.id))
    return {"message": "All sessions revoked"}


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


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    body: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Verify user email address using token from email.
    """
    from jose import JWTError, jwt

    from backend.app.core.security import get_secret_key

    token = body.token
    # Decode token manually to support custom type claims
    try:
        secret_key = get_secret_key()
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except JWTError:
        payload = None

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
        logger.error(f"Failed to send welcome email: {e}", exc_info=True)

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
    body: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Request password reset email.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == body.email))
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
        logger.error(f"Failed to send password reset email: {e}", exc_info=True)

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Reset password using token from email.
    """
    from jose import JWTError, jwt

    from backend.app.core.security import get_secret_key

    # Decode token manually to support custom type claims
    try:
        secret_key = get_secret_key()
        payload = jwt.decode(body.token, secret_key, algorithms=["HS256"])
    except JWTError:
        payload = None

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
    user.hashed_password = get_password_hash(body.new_password)
    await db.commit()

    return {"message": "Password reset successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete the current user's account (GDPR right to erasure).

    Anonymizes the user's email and deactivates the account. All associated
    experiments and iterations are permanently deleted via cascade.
    """
    # Anonymize PII — soft delete to preserve FK integrity during cascade
    current_user.email = f"deleted_{current_user.id}@deleted.invalid"
    current_user.full_name = None
    current_user.hashed_password = ""
    current_user.is_active = False
    current_user.stripe_customer_id = None
    current_user.stripe_subscription_id = None

    # Cascade delete is configured on experiments relationship so all
    # experiments, batch_runs, and iterations will be removed automatically.
    await db.delete(current_user)
    await db.commit()
