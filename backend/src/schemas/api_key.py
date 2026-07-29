"""
backend/src/schemas/api_key.py

Pydantic schemas for API key management.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key (request body)."""
    name: str = Field(..., min_length=1, max_length=255)


class ApiKeyResponse(BaseModel):
    """
    Schema for API key metadata (response).

    NEVER includes the plain key — only metadata.
    """
    id: str
    name: str
    last_used: datetime | None
    expires_at: datetime | None

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(BaseModel):
    """
    Schema for API key creation response.

    This is the ONLY time the plain key is ever shown.
    """
    id: str
    name: str
    key: str  # Plain key — shown once only
    expires_at: datetime | None
    created_at: str
