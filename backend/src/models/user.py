"""
backend/src/models/user.py

SQLAlchemy model for users.

Uses SQLAlchemy 2.0 declarative style with type hints.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.alert_rule import AlertRule
    from models.alert_history import AlertHistory
    from models.dashboard import Dashboard
    from models.api_key import ApiKey


class User(Base):
    """
    User account model.

    Supports three roles:
    - admin: Full access, can manage other users
    - editor: Can create alerts and dashboards
    - viewer: Read-only access
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="viewer",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    alert_rules: Mapped[list["AlertRule"]] = relationship(
        "AlertRule", back_populates="user", cascade="all, delete-orphan"
    )
    dashboards: Mapped[list["Dashboard"]] = relationship(
        "Dashboard", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, role={self.role!r})"
