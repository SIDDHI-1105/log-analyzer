"""
backend/src/models/log_entry.py

SQLAlchemy model for storing log entries in the database.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class LogEntry(Base):
    """
    A single log entry stored in the database.
    """

    __tablename__ = "log_entries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    level: Mapped[str] = mapped_column(
        String(20),
        default="INFO",
    )
    message: Mapped[str] = mapped_column(
        String(4000),
        nullable=False,
    )
    service: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    host: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    trace_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    span_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"LogEntry(id={self.id!r}, level={self.level!r}, message={self.message[:50]!r})"
