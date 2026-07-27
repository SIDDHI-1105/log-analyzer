"""
backend/src/models/alert_history.py

SQLAlchemy model for alert history (triggered alerts).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class AlertHistory(Base):
    """
    Record of when an alert rule was triggered.
    """

    __tablename__ = "alert_history"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rule_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("alert_rules.id"),
        nullable=False,
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="history")

    def __repr__(self) -> str:
        return f"AlertHistory(id={self.id!r}, rule_id={self.rule_id!r}, severity={self.severity!r})"