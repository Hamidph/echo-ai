"""
Security utilities for authentication and authorization.

This module provides JWT token generation/validation, password hashing,
and API key management.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.core.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The hashed password to check against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Use a secret key from settings (should be set in production)
    secret_key = getattr(settings, 'secret_key', 'your-secret-key-change-in-production')
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
        secret_key = getattr(settings, 'secret_key', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
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