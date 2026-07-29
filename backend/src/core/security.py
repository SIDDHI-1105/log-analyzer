"""
backend/src/core/security.py

Security utilities: password hashing, JWT token management, and API key hashing.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from core.config import get_settings

settings = get_settings()

# Password hashing context using Argon2 (recommended over bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject of the token (typically user id).
        expires_delta: Optional custom expiration time.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> str:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token string.

    Returns:
        The subject (user id) from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        subject: str | None = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return subject
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────
# API Key Utilities
# ─────────────────────────────────────────────

def generate_api_key() -> str:
    """
    Generate a cryptographically secure random API key.

    Format: la_<64 hex chars> (66 chars total)
    The 'la_' prefix makes it easy to identify in logs.
    """
    return "la_" + secrets.token_hex(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Uses the same Argon2 context as passwords.
    """
    return pwd_context.hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verify a plain API key against its stored hash.
    """
    return pwd_context.verify(plain_api_key, hashed_api_key)
