"""
backend/src/api/v1/api_keys.py

API Key management endpoints: generate, list, and revoke API keys.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from core.security import generate_api_key, hash_api_key
from models.api_key import ApiKey
from models.user import User
from schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyResponse

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("/", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    key_in: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Generate a new API key for the current user.

    ⚠️ The plain key is returned ONLY in this response.
    It cannot be retrieved again — store it securely.
    """
    # Generate and hash the key
    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)

    api_key = ApiKey(
        user_id=current_user.id,
        key_hash=key_hash,
        name=key_in.name,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": plain_key,
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/", response_model=list[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ApiKey]:
    """
    List all API keys for the current user.

    Returns metadata only — never the plain key.
    """
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == current_user.id)
        .all()
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Revoke (delete) an API key.
    """
    key = (
        db.query(ApiKey)
        .filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
        .first()
    )

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    db.delete(key)
    db.commit()
    return None
