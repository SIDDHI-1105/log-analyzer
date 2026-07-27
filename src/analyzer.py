"""
analyzer.py

Log analysis engine that transforms parsed log batches into insights.

This module implements the analysis layer of our pipeline:
    Parsed Logs (LogBatch) -> AnalysisResult

Key capabilities:
- Severity distribution (how many ERROR vs INFO vs WARN)
- Time-series analysis (when do errors spike?)
- Duplicate detection (what errors happen most often?)
- Service breakdown (which microservice has the most issues?)
- Alert evaluation (which rules are triggered?)

Design decisions:
- Pure functions where possible (easier to test)
- Efficient data structures (Counter, defaultdict)
- Lazy evaluation (compute on demand, cache results)
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any

from src.models import AlertRule, AnalysisResult, LogBatch, LogEntry, LogLevel


class LogAnalyzer:
    """
    Main analyzer that processes LogBatch objects and produces AnalysisResult.

    This is the core intelligence of the system. It answers questions like:
    - "How many errors occurred in the last hour?"
    - "Which service is failing the most?"
    - "What is the most common error message?"
    - "When was the peak error time?"

    Usage:
        batch = parser.parse_file("app.log")
        analyzer = LogAnalyzer(batch)
        result = analyzer.analyze()
        print(result.entries_by_level)
    """

    def __init__(self, batch: LogBatch):
        """
        Initialize with a parsed log batch.

        Args:
            batch: A LogBatch containing parsed LogEntry objects.
        """
        self.batch = batch
        self._entries_by_level: dict[str, int] | None = None
        self._most_common_messages: list[tuple[str, int]] | None = None
        self._top_services: list[tuple[str, int]] | None = None
        self._time_range: tuple[datetime | None, datetime | None] | None = None

    def analyze(self) -> AnalysisResult:
        """
        Run full analysis and return a complete AnalysisResult.

        This is the main entry point. It computes all statistics
        and returns them in a structured object.
        """
        return AnalysisResult(
            total_entries=len(self.batch.entries),
            entries_by_level=self.entries_by_level,
            most_common_messages=self.most_common_messages,
            time_range=self.time_range,
            top_services=self.top_services,
            average_message_length=self.average_message_length,
        )

    @property
    def entries_by_level(self) -> dict[str, int]:
        """
        Count of log entries grouped by severity level.

        Uses collections.Counter for O(n) efficiency.
        """
        if self._entries_by_level is None:
            counter = Counter(entry.level.value for entry in self.batch.entries)
            self._entries_by_level = dict(counter)
        return self._entries_by_level

    @property
    def most_common_messages(self) -> list[tuple[str, int]]:
        """
        Top 10 most frequently occurring log messages.

        This helps identify recurring issues that might need fixing.
        Uses Counter.most_common() which is implemented with a heap
        for O(n log k) efficiency where k=10.
        """
        if self._most_common_messages is None:
            counter = Counter(entry.message for entry in self.batch.entries)
            self._most_common_messages = counter.most_common(10)
        return self._most_common_messages

    @property
    def top_services(self) -> list[tuple[str, int]]:
        """
        Top services by log volume.

        Helps identify which microservices are most active or noisy.
        """
        if self._top_services is None:
            service_counts = Counter(
                entry.service or "unknown"
                for entry in self.batch.entries
            )
            self._top_services = service_counts.most_common(10)
        return self._top_services

    @property
    def time_range(self) -> tuple[datetime | None, datetime | None]:
        """
        The earliest and latest timestamps in the batch.

        Returns (None, None) if no entries have timestamps.
        """
        if self._time_range is None:
            timestamps = [
                entry.timestamp
                for entry in self.batch.entries
                if entry.timestamp is not None
            ]
            if timestamps:
                self._time_range = (min(timestamps), max(timestamps))
            else:
                self._time_range = (None, None)
        return self._time_range

    @property
    def average_message_length(self) -> float:
        """Average length of log messages in characters."""
        if not self.batch.entries:
            return 0.0
        total = sum(len(entry.message) for entry in self.batch.entries)
        return round(total / len(self.batch.entries), 2)

    def get_entries_by_level(self, level: LogLevel) -> list[LogEntry]:
        """
        Filter entries by severity level.

        Args:
            level: The LogLevel to filter by.

        Returns:
            List of LogEntry objects matching the level.
        """
        return [entry for entry in self.batch.entries if entry.level == level]

    def get_error_rate(self) -> float:
        """
        Calculate the percentage of entries that are ERROR or higher.

        This is a key metric for system health monitoring.
        """
        if not self.batch.entries:
            return 0.0

        error_levels = {LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.FATAL}
        error_count = sum(
            1 for entry in self.batch.entries if entry.level in error_levels
        )
        return round((error_count / len(self.batch.entries)) * 100, 2)

    def get_peak_hour(self) -> tuple[int, int] | None:
        """
        Find the hour with the most log entries.

        Returns:
            Tuple of (hour, count) or None if no timestamps.
        """
        hour_counts = Counter(
            entry.timestamp.hour
            for entry in self.batch.entries
            if entry.timestamp
        )
        if not hour_counts:
            return None
        return hour_counts.most_common(1)[0]

    def evaluate_alerts(self, rules: list[AlertRule]) -> list[AlertRule]:
        """
        Evaluate a list of alert rules against the current batch.

        Args:
            rules: Alert rules to check.

        Returns:
            List of rules that were triggered.
        """
        triggered = []
        for rule in rules:
            if not rule.enabled:
                continue

            # Count matching entries
            matching = [e for e in self.batch.entries if rule.matches(e)]
            if len(matching) >= rule.threshold:
                triggered.append(rule)

        return triggered


class TimeSeriesAnalyzer:
    """
    Analyzes logs over time to detect patterns and anomalies.

    This is used for:
    - Finding error spikes
    - Detecting unusual traffic patterns
    - Capacity planning
    """

    def __init__(self, entries: list[LogEntry]):
        self.entries = entries

    def get_entries_per_minute(self) -> dict[str, int]:
        """
        Group entries by minute and count them.

        Returns a dictionary like:
            {"2026-07-26 14:32": 15, "2026-07-26 14:33": 23, ...}
        """
        minute_counts: dict[str, int] = defaultdict(int)
        for entry in self.entries:
            if entry.timestamp:
                key = entry.timestamp.strftime("%Y-%m-%d %H:%M")
                minute_counts[key] += 1
        return dict(minute_counts)

    def get_error_spikes(
        self, window_minutes: int = 5, threshold_multiplier: float = 3.0
    ) -> list[dict[str, Any]]:
        """
        Detect time windows where error rate spikes above normal.

        A "spike" is defined as a window where the error count is
        threshold_multiplier times higher than the average.

        Args:
            window_minutes: Size of the sliding window.
            threshold_multiplier: How many times above average to trigger.

        Returns:
            List of spike events with time, count, and severity.
        """
        if not self.entries:
            return []

        # Group errors by time window
        error_entries = [
            e for e in self.entries
            if e.level in {LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.FATAL}
        ]

        if not error_entries:
            return []

        window_counts: dict[str, int] = defaultdict(int)
        for entry in error_entries:
            if entry.timestamp:
                # Round down to the nearest window
                minute = entry.timestamp.minute
                window_start = minute - (minute % window_minutes)
                window_time = entry.timestamp.replace(
                    minute=window_start, second=0, microsecond=0
                )
                key = window_time.strftime("%Y-%m-%d %H:%M")
                window_counts[key] += 1

        if not window_counts:
            return []

        avg_errors = sum(window_counts.values()) / len(window_counts)
        spikes = []

        for window, count in window_counts.items():
            if count > avg_errors * threshold_multiplier:
                spikes.append({
                    "window": window,
                    "error_count": count,
                    "average": round(avg_errors, 2),
                    "severity": "critical" if count > avg_errors * 5 else "warning",
                })

        # Sort by error count descending
        spikes.sort(key=lambda x: x["error_count"], reverse=True)
        return spikes
