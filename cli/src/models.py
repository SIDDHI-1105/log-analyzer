"""
models.py

Core data models for the Log Analyzer.
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class LogLevel(str, Enum):
    """Standard log severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class LogEntry(BaseModel):
    """A single parsed log line represented as a structured object."""

    timestamp: datetime | None = Field(default=None)
    level: LogLevel = Field(default=LogLevel.INFO)
    message: str = Field(...)
    service: str | None = Field(default=None)
    host: str | None = Field(default=None)
    trace_id: str | None = Field(default=None)
    span_id: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw_line: str = Field(...)

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Log message cannot be empty or whitespace only")
        return stripped

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            formats = [
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%d/%b/%Y:%H:%M:%S %z",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse timestamp: {value!r}")
        raise ValueError(f"Expected string or datetime, got {type(value).__name__}")

    def to_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        if self.timestamp:
            data["timestamp"] = self.timestamp.isoformat()
        return data

    def __str__(self) -> str:
        ts = self.timestamp.isoformat() if self.timestamp else "N/A"
        return f"[{ts}] {self.level.value}: {self.message}"

    def __repr__(self) -> str:
        msg = self.message[:50] + "..." if len(self.message) > 50 else self.message
        return f"LogEntry(timestamp={self.timestamp!r}, level={self.level.value!r}, message={msg!r})"


class LogBatch(BaseModel):
    """A collection of log entries with metadata about the batch."""

    entries: list[LogEntry] = Field(default_factory=list)
    source: str | None = Field(default=None)
    total_lines_read: int = Field(default=0, ge=0)
    parse_failures: int = Field(default=0, ge=0)

    @property
    def success_rate(self) -> float:
        if self.total_lines_read == 0:
            return 0.0
        successful = self.total_lines_read - self.parse_failures
        return round((successful / self.total_lines_read) * 100, 2)

    def add_entry(self, entry: LogEntry) -> None:
        self.entries.append(entry)

    def record_failure(self) -> None:
        self.parse_failures += 1
        self.total_lines_read += 1

    def record_success(self) -> None:
        self.total_lines_read += 1


class AlertRule(BaseModel):
    """Configuration for an alert that triggers when log conditions are met."""

    name: str = Field(..., min_length=1)
    severity: LogLevel = Field(...)
    threshold: int = Field(..., gt=0)
    time_window_seconds: int = Field(default=300, gt=0)
    match_pattern: str | None = Field(default=None)
    enabled: bool = Field(default=True)

    def matches(self, entry: LogEntry) -> bool:
        """
        Check if a log entry matches this alert rule.

        A match occurs when:
        1. The entry's severity is >= the rule's severity (numerically)
        2. AND the optional pattern matches the message (case-insensitive)
        """
        severity_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4,
            LogLevel.FATAL: 5,
        }
        if severity_order.get(entry.level, 0) < severity_order.get(self.severity, 0):
            return False

        if self.match_pattern:
            # Case-insensitive matching for better usability
            return bool(re.search(self.match_pattern, entry.message, re.IGNORECASE))
        return True


class AnalysisResult(BaseModel):
    """The output of analyzing a batch of logs."""

    total_entries: int = Field(default=0, ge=0)
    entries_by_level: dict[str, int] = Field(default_factory=dict)
    most_common_messages: list[tuple[str, int]] = Field(default_factory=list)
    time_range: tuple[datetime | None, datetime | None] = Field(default=(None, None))
    alerts_triggered: list[AlertRule] = Field(default_factory=list)
    top_services: list[tuple[str, int]] = Field(default_factory=list)
    average_message_length: float = Field(default=0.0)