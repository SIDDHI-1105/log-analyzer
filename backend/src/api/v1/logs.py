"""
backend/src/api/v1/logs.py

Log API endpoints: ingest, list, and search log entries.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_current_user_jwt_or_api_key
from core.database import get_db
from models.log_entry import LogEntry as LogEntryModel
from models.user import User
from schemas.log import LogBatchIngest, LogEntryResponse, LogIngestResponse
from services.alert_evaluator import evaluate_logs_for_alerts
from services.live_tail import live_tail_manager

router = APIRouter(prefix="/logs", tags=["Logs"])


async def _broadcast_logs(logs_data: list[dict]) -> None:
    """Broadcast multiple logs to WebSocket clients."""
    for log_data in logs_data:
        await live_tail_manager.broadcast_log(log_data)


@router.post("/ingest", response_model=LogIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_logs(
    batch: LogBatchIngest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_jwt_or_api_key),
) -> dict[str, int]:
    """
    Ingest a batch of log entries into the database.

    After ingestion, evaluates all active alert rules for the user
    and creates AlertHistory records if thresholds are breached.

    Also broadcasts new logs to connected WebSocket clients.

    Supports authentication via JWT token OR API key.
    """
    ingested = 0
    failed = 0
    created_logs: list[LogEntryModel] = []

    for entry in batch.entries:
        try:
            log = LogEntryModel(
                timestamp=entry.timestamp,
                level=entry.level.upper(),
                message=entry.message,
                service=entry.service,
                host=entry.host,
                trace_id=entry.trace_id,
                span_id=entry.span_id,
                extra_data=entry.metadata,
            )
            db.add(log)
            created_logs.append(log)
            ingested += 1
        except Exception:
            failed += 1

    db.commit()

    # Refresh created logs to get their IDs and timestamps
    for log in created_logs:
        db.refresh(log)

    # Evaluate alerts against the newly ingested logs
    if created_logs:
        evaluate_logs_for_alerts(db, created_logs, current_user.id)

    # Broadcast logs to WebSocket clients via background task
    logs_data = []
    for log in created_logs:
        logs_data.append({
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "level": log.level,
            "message": log.message,
            "service": log.service,
            "host": log.host,
            "trace_id": log.trace_id,
            "span_id": log.span_id,
            "extra_data": log.extra_data,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })
    
    if logs_data:
        background_tasks.add_task(_broadcast_logs, logs_data)

    return {"ingested": ingested, "failed": failed}


@router.get("/", response_model=list[LogEntryResponse])
def list_logs(
    skip: int = 0,
    limit: int = 50,
    level: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LogEntryModel]:
    """
    List log entries with optional filtering.

    Requires authentication via JWT token.
    """
    query = db.query(LogEntryModel)
    if level:
        query = query.filter(LogEntryModel.level == level.upper())
    return query.order_by(LogEntryModel.created_at.desc()).offset(skip).limit(limit).all()
