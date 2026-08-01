"""
backend/src/schemas/stats.py

Pydantic schemas for dashboard statistics.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LevelCount(BaseModel):
    """Count of logs for a specific level."""
    level: str
    count: int


class ServiceCount(BaseModel):
    """Count of logs for a specific service."""
    service: str
    count: int


class StatsResponse(BaseModel):
    """Overall statistics for the dashboard."""
    total_logs: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    critical_count: int
    error_rate: float
    logs_by_level: list[LevelCount]
    logs_by_service: list[ServiceCount]
    unique_services: int
    time_range_hours: int


class TimeSeriesPoint(BaseModel):
    """A single point in a time series."""
    timestamp: datetime
    count: int


class TimeSeriesResponse(BaseModel):
    """Time series data for charting."""
    interval: str  # "hour" or "day"
    points: list[TimeSeriesPoint]
