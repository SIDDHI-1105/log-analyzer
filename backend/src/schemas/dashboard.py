"""
backend/src/schemas/dashboard.py

Pydantic schemas for saved dashboards.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DashboardBase(BaseModel):
    """Base fields shared across dashboard schemas."""
    name: str = Field(..., min_length=1, max_length=255)
    widgets: dict[str, Any] = Field(default_factory=dict)


class DashboardCreate(DashboardBase):
    """Schema for creating a new dashboard (request body)."""
    pass


class DashboardUpdate(BaseModel):
    """Schema for updating an existing dashboard (partial update)."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    widgets: dict[str, Any] | None = None


class DashboardResponse(DashboardBase):
    """Schema for dashboard response (includes DB fields)."""
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
