"""
backend/src/api/v1/stats.py

Dashboard statistics API endpoints.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.log_entry import LogEntry as LogEntryModel
from models.user import User
from schemas.stats import (
    LevelCount,
    ServiceCount,
    StatsResponse,
    TimeSeriesPoint,
    TimeSeriesResponse,
)

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/", response_model=StatsResponse)
def get_stats(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsResponse:
    """
    Get overall statistics for the dashboard.

    - hours: Time range to look back (24, 168 for 7d, 720 for 30d)
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    # Base query for the time range
    base_query = db.query(LogEntryModel).filter(LogEntryModel.created_at >= since)

    # Total logs in range
    total_logs = base_query.count()

    # Count by level
    level_counts = (
        db.query(LogEntryModel.level, func.count(LogEntryModel.id))
        .filter(LogEntryModel.created_at >= since)
        .group_by(LogEntryModel.level)
        .all()
    )

    level_map = {row[0].upper(): row[1] for row in level_counts}
    error_count = level_map.get("ERROR", 0)
    warning_count = level_map.get("WARNING", 0)
    info_count = level_map.get("INFO", 0)
    debug_count = level_map.get("DEBUG", 0)
    critical_count = level_map.get("CRITICAL", 0)

    # Error rate
    error_rate = (error_count + critical_count) / total_logs * 100 if total_logs > 0 else 0.0

    # Logs by level (formatted)
    logs_by_level = [
        LevelCount(level=level, count=level_map.get(level, 0))
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    ]

    # Logs by service (top 10)
    service_counts = (
        db.query(LogEntryModel.service, func.count(LogEntryModel.id))
        .filter(LogEntryModel.created_at >= since)
        .filter(LogEntryModel.service.isnot(None))
        .group_by(LogEntryModel.service)
        .order_by(func.count(LogEntryModel.id).desc())
        .limit(10)
        .all()
    )

    logs_by_service = [
        ServiceCount(service=row[0] or "unknown", count=row[1])
        for row in service_counts
    ]

    # Unique services count
    unique_services = (
        db.query(func.count(func.distinct(LogEntryModel.service)))
        .filter(LogEntryModel.created_at >= since)
        .scalar()
        or 0
    )

    return StatsResponse(
        total_logs=total_logs,
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        debug_count=debug_count,
        critical_count=critical_count,
        error_rate=round(error_rate, 2),
        logs_by_level=logs_by_level,
        logs_by_service=logs_by_service,
        unique_services=unique_services,
        time_range_hours=hours,
    )


@router.get("/timeseries", response_model=TimeSeriesResponse)
def get_timeseries(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimeSeriesResponse:
    """
    Get time-series data for charting log volume over time.

    - hours <= 48: bucket by hour
    - hours > 48: bucket by day
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    interval = "hour" if hours <= 48 else "day"

    if interval == "hour":
        # Group by hour using date_trunc
        results = (
            db.query(
                func.date_trunc("hour", LogEntryModel.created_at).label("bucket"),
                func.count(LogEntryModel.id).label("count"),
            )
            .filter(LogEntryModel.created_at >= since)
            .group_by("bucket")
            .order_by("bucket")
            .all()
        )
    else:
        # Group by day
        results = (
            db.query(
                func.date_trunc("day", LogEntryModel.created_at).label("bucket"),
                func.count(LogEntryModel.id).label("count"),
            )
            .filter(LogEntryModel.created_at >= since)
            .group_by("bucket")
            .order_by("bucket")
            .all()
        )

    points = [
        TimeSeriesPoint(timestamp=row[0], count=row[1])
        for row in results
        if row[0] is not None
    ]

    return TimeSeriesResponse(
        interval=interval,
        points=points,
    )
