"""
backend/src/api/v1/logs.py

Log API endpoints: ingest, list, and search log entries.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.log_entry import LogEntry as LogEntryModel
from models.user import User
from schemas.log import LogBatchIngest, LogEntryResponse, LogIngestResponse

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/ingest", response_model=LogIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_logs(
    batch: LogBatchIngest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    """
    Ingest a batch of log entries into the database.

    Requires authentication via Bearer token.
    """
    ingested = 0
    failed = 0

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
            ingested += 1
        except Exception:
            failed += 1

    db.commit()
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

    Requires authentication via Bearer token.
    """
    query = db.query(LogEntryModel)
    if level:
        query = query.filter(LogEntryModel.level == level.upper())
    return query.order_by(LogEntryModel.created_at.desc()).offset(skip).limit(limit).all()
