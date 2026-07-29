"""
backend/src/api/v1/export.py

Export API endpoints: download logs and alerts in CSV, JSON, or HTML.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.user import User
from services.export_service import ExportRegistry, query_logs_for_export, query_alerts_for_export

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/logs")
def export_logs(
    format: Literal["json", "csv", "html"] = Query(default="json", description="Export format"),
    level: str | None = Query(default=None, description="Filter by log level"),
    service: str | None = Query(default=None, description="Filter by service name"),
    start_date: datetime | None = Query(default=None, description="Filter logs from this date (ISO 8601)"),
    end_date: datetime | None = Query(default=None, description="Filter logs up to this date (ISO 8601)"),
    limit: int = Query(default=1000, ge=1, le=10000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export log entries in the requested format (JSON, CSV, or HTML).

    Supports filtering by level, service, and date range.
    """
    try:
        exporter = ExportRegistry.get_exporter(format)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    logs = query_logs_for_export(
        db=db,
        user_id=current_user.id,
        level=level,
        service=service,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    content = exporter.export_logs(logs)

    filename = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{exporter.get_extension()}"

    return PlainTextResponse(
        content=content,
        media_type=exporter.get_mime_type(),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/alerts")
def export_alerts(
    format: Literal["json", "csv", "html"] = Query(default="json", description="Export format"),
    rule_id: str | None = Query(default=None, description="Filter by alert rule ID"),
    start_date: datetime | None = Query(default=None, description="Filter alerts from this date (ISO 8601)"),
    end_date: datetime | None = Query(default=None, description="Filter alerts up to this date (ISO 8601)"),
    limit: int = Query(default=1000, ge=1, le=10000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export alert history in the requested format (JSON, CSV, or HTML).

    Supports filtering by rule ID and date range.
    """
    try:
        exporter = ExportRegistry.get_exporter(format)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    alerts = query_alerts_for_export(
        db=db,
        user_id=current_user.id,
        rule_id=rule_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    content = exporter.export_alerts(alerts)

    filename = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{exporter.get_extension()}"

    return PlainTextResponse(
        content=content,
        media_type=exporter.get_mime_type(),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
