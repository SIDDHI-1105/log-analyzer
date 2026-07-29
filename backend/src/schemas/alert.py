"""
backend/src/schemas/alert.py

Pydantic schemas for alert rules and alert history.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Alert Rule Schemas
# ─────────────────────────────────────────────

class AlertRuleBase(BaseModel):
    """Base fields shared across alert rule schemas."""
    name: str = Field(..., min_length=1, max_length=255)
    severity: str = Field(..., pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    threshold: int = Field(..., ge=1)
    time_window_seconds: int = Field(default=300, ge=1)
    match_pattern: str | None = Field(default=None, max_length=500)
    notification_channels: list[str] = Field(default_factory=list)
    is_active: bool = True


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating a new alert rule (request body)."""
    pass


class AlertRuleUpdate(BaseModel):
    """Schema for updating an existing alert rule (partial update)."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    severity: str | None = Field(default=None, pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    threshold: int | None = Field(default=None, ge=1)
    time_window_seconds: int | None = Field(default=None, ge=1)
    match_pattern: str | None = Field(default=None, max_length=500)
    notification_channels: list[str] | None = None
    is_active: bool | None = None


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule response (includes DB fields)."""
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Alert History Schemas
# ─────────────────────────────────────────────

class AlertHistoryResponse(BaseModel):
    """Schema for alert history (triggered alert) response."""
    id: str
    rule_id: str
    triggered_at: datetime
    resolved_at: datetime | None
    severity: str
    details: dict[str, Any] | None

    class Config:
        from_attributes = True


class AlertRuleWithHistoryResponse(AlertRuleResponse):
    """Schema for alert rule response including its history."""
    history: list[AlertHistoryResponse] = []

    class Config:
        from_attributes = True
