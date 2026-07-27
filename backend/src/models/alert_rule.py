"""
backend/src/models/alert_rule.py

SQLAlchemy model for alert rules.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.alert_history import AlertHistory


class AlertRule(Base):
    """
    Configuration for an alert that triggers when log conditions are met.
    """

    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    time_window_seconds: Mapped[int] = mapped_column(
        Integer,
        default=300,
    )
    match_pattern: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    notification_channels: Mapped[str] = mapped_column(
        String(1000),
        default="[]",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="alert_rules")
    history: Mapped[list["AlertHistory"]] = relationship(
        "AlertHistory", back_populates="rule", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"AlertRule(id={self.id!r}, name={self.name!r}, severity={self.severity!r})"
