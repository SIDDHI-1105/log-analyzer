"""
reporters.py

Report generation engine that formats analysis results for different consumers.

This module uses the Strategy Pattern (same as parsers) to support
multiple output formats behind a common interface:

    BaseReporter (ABC)
    ├── ConsoleReporter  -> Pretty colored terminal tables
    ├── JsonReporter     -> Machine-readable JSON
    ├── CsvReporter      -> Spreadsheet-compatible CSV
    └── HtmlReporter     -> Web-viewable HTML report

Adding a new format (e.g., PDF, Markdown, Slack message) requires
only implementing BaseReporter — no changes to existing code.
"""

from __future__ import annotations

import csv
import io
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.models import AnalysisResult, LogBatch


class BaseReporter(ABC):
    """Abstract base class for all report generators."""

    @abstractmethod
    def generate(self, result: AnalysisResult, batch: LogBatch | None = None) -> str:
        """Generate a report from analysis results."""
        ...

    @abstractmethod
    def get_extension(self) -> str:
        """Return the file extension for this format (e.g., '.json')."""
        ...

    @abstractmethod
    def get_mime_type(self) -> str:
        """Return the MIME type for HTTP responses (e.g., 'application/json')."""
        ...


class ConsoleReporter(BaseReporter):
    """Pretty terminal output."""

    def generate(self, result: AnalysisResult, batch: LogBatch | None = None) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("LOG ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Total Entries: {result.total_entries}")
        lines.append("")

        lines.append("SEVERITY DISTRIBUTION")
        lines.append("-" * 40)
        for level, count in sorted(result.entries_by_level.items()):
            bar = "█" * min(count, 40)
            lines.append(f"  {level:12} {count:5} {bar}")
        lines.append("")

        if result.top_services:
            lines.append("TOP SERVICES")
            lines.append("-" * 40)
            for service, count in result.top_services:
                lines.append(f"  {service:30} {count}")
            lines.append("")

        if result.most_common_messages:
            lines.append("MOST COMMON MESSAGES")
            lines.append("-" * 40)
            for msg, count in result.most_common_messages:
                short = msg[:45] + "..." if len(msg) > 45 else msg
                lines.append(f"  {count:3}x  {short}")
            lines.append("")

        if result.time_range[0] and result.time_range[1]:
            lines.append("TIME RANGE")
            lines.append("-" * 40)
            lines.append(f"  From: {result.time_range[0]}")
            lines.append(f"  To:   {result.time_range[1]}")
            lines.append("")

        if batch:
            lines.append("PARSE STATISTICS")
            lines.append("-" * 40)
            lines.append(f"  Source:     {batch.source}")
            lines.append(f"  Lines read: {batch.total_lines_read}")
            lines.append(f"  Failures:   {batch.parse_failures}")
            lines.append(f"  Success:    {batch.success_rate}%")
            lines.append("")

        if result.alerts_triggered:
            lines.append("ALERTS TRIGGERED")
            lines.append("-" * 40)
            for alert in result.alerts_triggered:
                lines.append(f"  ! {alert.name} (threshold: {alert.threshold})")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def get_extension(self) -> str:
        return ".txt"

    def get_mime_type(self) -> str:
        return "text/plain"


class JsonReporter(BaseReporter):
    """JSON format for APIs and integrations."""

    def generate(self, result: AnalysisResult, batch: LogBatch | None = None) -> str:
        data: dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_entries": result.total_entries,
                "entries_by_level": result.entries_by_level,
                "average_message_length": result.average_message_length,
            },
            "top_services": [
                {"service": s, "count": c} for s, c in result.top_services
            ],
            "most_common_messages": [
                {"message": m, "count": c} for m, c in result.most_common_messages
            ],
            "time_range": {
                "from": result.time_range[0].isoformat() if result.time_range[0] else None,
                "to": result.time_range[1].isoformat() if result.time_range[1] else None,
            },
        }
        if batch:
            data["parse_statistics"] = {
                "source": batch.source,
                "total_lines_read": batch.total_lines_read,
                "parse_failures": batch.parse_failures,
                "success_rate": batch.success_rate,
            }
        return json.dumps(data, indent=2)

    def get_extension(self) -> str:
        return ".json"

    def get_mime_type(self) -> str:
        return "application/json"


class CsvReporter(BaseReporter):
    """CSV format for spreadsheets."""

    def generate(self, result: AnalysisResult, batch: LogBatch | None = None) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Entries", result.total_entries])
        writer.writerow(["Average Message Length", result.average_message_length])
        writer.writerow([])
        writer.writerow(["Severity", "Count"])
        for level, count in sorted(result.entries_by_level.items()):
            writer.writerow([level, count])
        writer.writerow([])
        writer.writerow(["Service", "Count"])
        for service, count in result.top_services:
            writer.writerow([service, count])
        writer.writerow([])
        writer.writerow(["Message", "Count"])
        for msg, count in result.most_common_messages:
            writer.writerow([msg, count])
        return output.getvalue()

    def get_extension(self) -> str:
        return ".csv"

    def get_mime_type(self) -> str:
        return "text/csv"


class HtmlReporter(BaseReporter):
    """HTML report with basic styling."""

    def generate(self, result: AnalysisResult, batch: LogBatch | None = None) -> str:
        colors = {
            "DEBUG": "#6c757d",
            "INFO": "#0d6efd",
            "WARNING": "#ffc107",
            "ERROR": "#dc3545",
            "CRITICAL": "#212529",
            "FATAL": "#000000",
        }

        severity_rows = ""
        for level, count in sorted(result.entries_by_level.items()):
            color = colors.get(level, "#6c757d")
            severity_rows += f'<tr><td><span style="color:{color};font-weight:bold;">{level}</span></td><td>{count}</td></tr>\n'

        service_rows = ""
        for service, count in result.top_services:
            service_rows += f"<tr><td>{service}</td><td>{count}</td></tr>\n"

        message_rows = ""
        for msg, count in result.most_common_messages:
            message_rows += f"<tr><td>{msg}</td><td>{count}</td></tr>\n"

        time_from = result.time_range[0].isoformat() if result.time_range[0] else "N/A"
        time_to = result.time_range[1].isoformat() if result.time_range[1] else "N/A"

        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Log Analysis Report</title>
<style>
body {{ font-family: sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
h1 {{ color: #212529; border-bottom: 2px solid #0d6efd; padding-bottom: 10px; }}
h2 {{ color: #495057; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
th {{ background: #f8f9fa; font-weight: 600; }}
.summary {{ background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
</style>
</head>
<body>
<h1>Log Analysis Report</h1>
<div class="summary"><strong>Generated:</strong> {datetime.now().isoformat()}<br>
<strong>Total Entries:</strong> {result.total_entries}<br>
<strong>Time Range:</strong> {time_from} to {time_to}</div>

<h2>Severity Distribution</h2>
<table><tr><th>Level</th><th>Count</th></tr>{severity_rows}</table>

<h2>Top Services</h2>
<table><tr><th>Service</th><th>Count</th></tr>{service_rows}</table>

<h2>Most Common Messages</h2>
<table><tr><th>Message</th><th>Count</th></tr>{message_rows}</table>
</body>
</html>"""

        return html

    def get_extension(self) -> str:
        return ".html"

    def get_mime_type(self) -> str:
        return "text/html"


class ReporterRegistry:
    """Factory for getting reporters by name."""

    _reporters: dict[str, type[BaseReporter]] = {
        "console": ConsoleReporter,
        "json": JsonReporter,
        "csv": CsvReporter,
        "html": HtmlReporter,
    }

    @classmethod
    def get_reporter(cls, name: str) -> BaseReporter:
        reporter_class = cls._reporters.get(name.lower())
        if not reporter_class:
            available = ", ".join(cls._reporters.keys())
            raise ValueError(f"Unknown reporter '{name}'. Available: {available}")
        return reporter_class()

    @classmethod
    def register(cls, name: str, reporter_class: type[BaseReporter]) -> None:
        cls._reporters[name.lower()] = reporter_class

    @classmethod
    def list_reporters(cls) -> list[str]:
        return list(cls._reporters.keys())