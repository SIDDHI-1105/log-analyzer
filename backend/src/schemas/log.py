"""
backend/src/schemas/log.py

Pydantic schemas for log entries and batches.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogEntryCreate(BaseModel):
    """Schema for creating a single log entry."""
    timestamp: datetime | None = None
    level: str = Field(default="INFO")
    message: str
    service: str | None = None
    host: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LogBatchIngest(BaseModel):
    """Schema for ingesting a batch of log entries."""
    entries: list[LogEntryCreate]


class LogEntryResponse(BaseModel):
    """Schema for a log entry response."""
    id: str
    timestamp: datetime | None
    level: str
    message: str
    service: str | None
    host: str | None
    trace_id: str | None
    span_id: str | None
    extra_data: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True


class LogIngestResponse(BaseModel):
    """Schema for log ingestion response."""
    ingested: int
    failed: int = 0
