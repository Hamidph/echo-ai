"""
Security utilities for authentication and authorization.

This module provides JWT token generation/validation, password hashing,
and API key management.

Security best practices implemented:
- Short-lived access tokens (15 minutes)
- Refresh tokens for extended sessions (7 days)
- Bcrypt password hashing with salt
- Secure API key generation
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from backend.app.core.config import get_settings

settings = get_settings()

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes (short-lived for security)
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days (for refresh tokens)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The hashed password to check against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


    return encoded_jwt


def get_secret_key() -> str:
    """
    Get the secret key, enforcing security in production.
    
    Returns:
        str: The secret key.
        
    Raises:
        ValueError: If key is insecure in production.
    """
    key = getattr(settings, 'secret_key', 'your-secret-key-change-in-production')
    
    # Check for insecure default
    if key == 'your-secret-key-change-in-production':
        if not settings.testing_mode:
            raise ValueError("FATAL: Insecure SECRET_KEY used in production mode! Set strictly in .env")
        else:
            # In testing, we allow it but warn
            pass
            
    return key


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically user_id and email).
        expires_delta: Optional custom expiration time.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    secret_key = get_secret_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Refresh tokens are used to obtain new access tokens without re-authenticating.
    They should be stored securely (httpOnly cookies) and have longer TTL.

    Args:
        data: Data to encode in the token (typically user_id).

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    secret_key = get_secret_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode.

    Returns:
        dict | None: The decoded token payload, or None if invalid.
    """
    try:
        secret_key = get_secret_key()
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])

        # Verify token type
        token_type = payload.get("type")
        if token_type != "access":
            return None

        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT refresh token.

    Args:
        token: The JWT refresh token to decode.

    Returns:
        dict | None: The decoded token payload, or None if invalid.
    """
    try:
        secret_key = get_secret_key()
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])

        # Verify token type
        token_type = payload.get("type")
        if token_type != "refresh":
            return None

        return payload
    except JWTError:
        return None


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key.

    Returns:
        tuple[str, str]: (raw_key, hashed_key)
            - raw_key: The unhashed API key to show to the user (only shown once)
            - hashed_key: The hashed API key to store in the database
    """
    # Generate a secure random API key
    raw_key = f"sk_live_{secrets.token_urlsafe(32)}"
    hashed_key = get_password_hash(raw_key)
    return raw_key, hashed_key


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hashed version.

    Args:
        raw_key: The raw API key provided by the user.
        hashed_key: The hashed API key from the database.

    Returns:
        bool: True if the key matches, False otherwise.
    """
    return verify_password(raw_key, hashed_key)


def get_api_key_prefix(key: str) -> str:
    """
    Get the display prefix for an API key.

    Args:
        key: The raw API key.

    Returns:
        str: The first 12 characters of the key for display.
    """
    return key[:12] + "..."
