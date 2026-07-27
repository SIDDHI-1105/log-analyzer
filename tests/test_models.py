"""
test_models.py

Tests for the core data models.

These tests verify:
- Pydantic validation works correctly
- LogEntry handles various timestamp formats
- LogBatch tracks statistics accurately
- AlertRule matching logic is correct
"""

from datetime import datetime

import pytest

from src.models import AlertRule, LogBatch, LogEntry, LogLevel


class TestLogEntry:
    """Tests for the LogEntry model."""

    def test_create_valid_entry(self):
        """A normal log entry should be created without errors."""
        entry = LogEntry(
            timestamp="2026-07-26T14:32:15",
            level="ERROR",
            message="Database connection failed",
            service="payment-service",
            raw_line="2026-07-26 14:32:15 ERROR Database connection failed",
        )
        assert entry.level == LogLevel.ERROR
        assert entry.message == "Database connection failed"
        assert entry.service == "payment-service"
        assert entry.timestamp == datetime(2026, 7, 26, 14, 32, 15)

    def test_create_with_datetime_object(self):
        """Should accept datetime objects directly."""
        now = datetime.now()
        entry = LogEntry(
            timestamp=now,
            level=LogLevel.INFO,
            message="Test",
            raw_line="INFO Test",
        )
        assert entry.timestamp == now

    def test_empty_message_rejected(self):
        """Empty or whitespace-only messages should raise ValidationError."""
        with pytest.raises(Exception):
            LogEntry(message="", raw_line="")

        with pytest.raises(Exception):
            LogEntry(message="   ", raw_line="   ")

    def test_default_level_is_info(self):
        """If no level is provided, default to INFO."""
        entry = LogEntry(message="Something happened", raw_line="Something happened")
        assert entry.level == LogLevel.INFO

    def test_str_representation(self):
        """String output should be human-readable."""
        entry = LogEntry(
            timestamp="2026-07-26T14:32:15",
            level="ERROR",
            message="Fail",
            raw_line="...",
        )
        assert "2026-07-26T14:32:15" in str(entry)
        assert "ERROR" in str(entry)
        assert "Fail" in str(entry)

    def test_to_dict_serializes_timestamp(self):
        """to_dict() should convert datetime to ISO string."""
        entry = LogEntry(
            timestamp="2026-07-26T14:32:15",
            level="INFO",
            message="Test",
            raw_line="...",
        )
        d = entry.to_dict()
        assert d["timestamp"] == "2026-07-26T14:32:15"
        assert d["level"] == "INFO"


class TestLogBatch:
    """Tests for the LogBatch model."""

    def test_empty_batch(self):
        """An empty batch should have zero stats."""
        batch = LogBatch()
        assert batch.total_lines_read == 0
        assert batch.parse_failures == 0
        assert batch.success_rate == 0.0

    def test_add_entry_increments_count(self):
        """Adding an entry should track it correctly."""
        batch = LogBatch()
        entry = LogEntry(message="Test", raw_line="Test")
        batch.add_entry(entry)
        batch.record_success()
        assert batch.total_lines_read == 1
        assert len(batch.entries) == 1
        assert batch.success_rate == 100.0

    def test_failure_tracking(self):
        """Failed parses should be tracked separately."""
        batch = LogBatch()
        batch.record_failure()
        assert batch.total_lines_read == 1
        assert batch.parse_failures == 1
        assert batch.success_rate == 0.0

    def test_mixed_success_and_failure(self):
        """Success rate should be calculated correctly."""
        batch = LogBatch()
        batch.record_success()
        batch.record_success()
        batch.record_failure()
        assert batch.success_rate == 66.67


class TestAlertRule:
    """Tests for the AlertRule model."""

    def test_matches_by_severity(self):
        """Should match entries at or above the rule's severity."""
        rule = AlertRule(
            name="Error Alert",
            severity=LogLevel.ERROR,
            threshold=1,
        )
        error_entry = LogEntry(level="ERROR", message="Fail", raw_line="...")
        info_entry = LogEntry(level="INFO", message="OK", raw_line="...")

        assert rule.matches(error_entry) is True
        assert rule.matches(info_entry) is False

    def test_matches_with_pattern(self):
        """Should match only when pattern is in the message."""
        rule = AlertRule(
            name="DB Alert",
            severity=LogLevel.ERROR,
            threshold=1,
            match_pattern="database",
        )
        match_entry = LogEntry(level="ERROR", message="Database timeout", raw_line="...")
        no_match_entry = LogEntry(level="ERROR", message="Network timeout", raw_line="...")

        assert rule.matches(match_entry) is True
        assert rule.matches(no_match_entry) is False

    def test_critical_matches_error_rule(self):
        """CRITICAL is higher than ERROR, so it should match an ERROR rule."""
        rule = AlertRule(
            name="Error Alert",
            severity=LogLevel.ERROR,
            threshold=1,
        )
        critical_entry = LogEntry(level="CRITICAL", message="System down", raw_line="...")

        assert rule.matches(critical_entry) is True