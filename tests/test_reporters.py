"""
test_reporters.py

Tests for all report generators.

Verifies that each reporter produces valid, well-formed output.
"""

from datetime import datetime

from src.models import AnalysisResult, LogBatch, LogEntry
from src.reporters import (
    ConsoleReporter,
    CsvReporter,
    HtmlReporter,
    JsonReporter,
    ReporterRegistry,
)


def make_result():
    """Helper to create a sample AnalysisResult."""
    return AnalysisResult(
        total_entries=3,
        entries_by_level={"ERROR": 2, "INFO": 1},
        most_common_messages=[("Database timeout", 2), ("OK", 1)],
        time_range=(datetime(2026, 7, 26, 14, 30), datetime(2026, 7, 26, 14, 35)),
        top_services=[("payment-service", 2), ("auth-service", 1)],
        average_message_length=15.0,
    )


class TestConsoleReporter:
    """Tests for console output."""

    def test_generates_report(self):
        """Should produce a non-empty string with key sections."""
        reporter = ConsoleReporter()
        result = make_result()
        output = reporter.generate(result)
        assert "LOG ANALYSIS REPORT" in output
        assert "ERROR" in output
        assert "INFO" in output
        assert "payment-service" in output

    def test_includes_batch_stats(self):
        """Should include parse statistics when batch is provided."""
        reporter = ConsoleReporter()
        result = make_result()
        batch = LogBatch(source="test.log", total_lines_read=5, parse_failures=1)
        output = reporter.generate(result, batch)
        assert "test.log" in output
        assert "80.0%" in output  # 4/5 success


class TestJsonReporter:
    """Tests for JSON output."""

    def test_valid_json(self):
        """Output should be parseable JSON."""
        import json

        reporter = JsonReporter()
        result = make_result()
        output = reporter.generate(result)
        data = json.loads(output)
        assert data["summary"]["total_entries"] == 3
        assert data["summary"]["entries_by_level"]["ERROR"] == 2

    def test_includes_time_range(self):
        """Should include formatted time range."""
        reporter = JsonReporter()
        result = make_result()
        output = reporter.generate(result)
        import json

        data = json.loads(output)
        assert data["time_range"]["from"] is not None


class TestCsvReporter:
    """Tests for CSV output."""

    def test_has_headers(self):
        """Should include column headers."""
        reporter = CsvReporter()
        result = make_result()
        output = reporter.generate(result)
        assert "Metric,Value" in output
        assert "Severity,Count" in output

    def test_contains_data(self):
        """Should include actual data rows."""
        reporter = CsvReporter()
        result = make_result()
        output = reporter.generate(result)
        assert "ERROR,2" in output
        assert "payment-service,2" in output


class TestHtmlReporter:
    """Tests for HTML output."""

    def test_valid_html_structure(self):
        """Should be a complete HTML document."""
        reporter = HtmlReporter()
        result = make_result()
        output = reporter.generate(result)
        assert "<!DOCTYPE html>" in output
        assert "<html>" in output
        assert "</html>" in output

    def test_contains_data(self):
        """Should include the analysis data."""
        reporter = HtmlReporter()
        result = make_result()
        output = reporter.generate(result)
        assert "ERROR" in output
        assert "payment-service" in output


class TestReporterRegistry:
    """Tests for the reporter factory."""

    def test_list_reporters(self):
        """Should return all available reporters."""
        reporters = ReporterRegistry.list_reporters()
        assert "console" in reporters
        assert "json" in reporters
        assert "csv" in reporters
        assert "html" in reporters

    def test_get_reporter(self):
        """Should return correct reporter instances."""
        assert isinstance(ReporterRegistry.get_reporter("json"), JsonReporter)
        assert isinstance(ReporterRegistry.get_reporter("csv"), CsvReporter)

    def test_get_reporter_invalid(self):
        """Should raise ValueError for unknown reporters."""
        import pytest

        with pytest.raises(ValueError):
            ReporterRegistry.get_reporter("pdf")