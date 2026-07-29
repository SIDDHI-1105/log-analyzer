"""
backend/src/api/deps.py

FastAPI dependencies for authentication and database access.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token, verify_api_key
from models.api_key import ApiKey
from models.user import User

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency to get the currently authenticated user via JWT.

    Extracts the JWT token from the Authorization header,
    validates it, and returns the corresponding User object.

    Raises 401 if the token is invalid or the user doesn't exist.
    """
    user_id = decode_access_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


def get_current_user_by_api_key(
    api_key: str,
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate a user by API key.

    Looks up the API key hash in the database and returns
    the associated user if valid.

    Raises 401 if the key is invalid or expired.
    """
    all_keys = db.query(ApiKey).filter(
        ApiKey.expires_at.is_(None) | (ApiKey.expires_at > datetime.now(timezone.utc))
    ).all()

    for key_record in all_keys:
        if verify_api_key(api_key, key_record.key_hash):
            # Update last_used
            key_record.last_used = datetime.now(timezone.utc)
            db.commit()

            user = db.query(User).filter(User.id == key_record.user_id).first()
            if user and user.is_active:
                return user
            break

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired API key",
    )


def get_current_user_jwt_or_api_key(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate via JWT token OR API key.

    Tries JWT first (standard Bearer token). If that fails,
    falls back to treating the token as an API key.

    This allows endpoints to accept either authentication method.
    """
    # Try JWT first
    try:
        user_id = decode_access_token(token)
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user
    except HTTPException:
        pass  # Not a valid JWT, try API key

    # Try API key
    all_keys = db.query(ApiKey).filter(
        ApiKey.expires_at.is_(None) | (ApiKey.expires_at > datetime.now(timezone.utc))
    ).all()

    for key_record in all_keys:
        if verify_api_key(token, key_record.key_hash):
            key_record.last_used = datetime.now(timezone.utc)
            db.commit()

            user = db.query(User).filter(User.id == key_record.user_id).first()
            if user and user.is_active:
                return user
            break

    # Neither worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
