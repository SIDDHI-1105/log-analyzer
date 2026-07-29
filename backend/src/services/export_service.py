"""
backend/src/services/export_service.py

Export service for generating downloadable reports in multiple formats.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from models.alert_history import AlertHistory
from models.alert_rule import AlertRule
from models.log_entry import LogEntry


class BaseExporter:
    """Base class for export formatters."""

    def export_logs(self, logs: list[LogEntry]) -> str:
        raise NotImplementedError

    def export_alerts(self, alerts: list[AlertHistory]) -> str:
        raise NotImplementedError

    def get_mime_type(self) -> str:
        raise NotImplementedError

    def get_extension(self) -> str:
        raise NotImplementedError


class JsonExporter(BaseExporter):
    """JSON export formatter."""

    def export_logs(self, logs: list[LogEntry]) -> str:
        data = [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "level": log.level,
                "message": log.message,
                "service": log.service,
                "host": log.host,
                "trace_id": log.trace_id,
                "span_id": log.span_id,
                "extra_data": log.extra_data,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
        return json.dumps(data, indent=2, default=str)

    def export_alerts(self, alerts: list[AlertHistory]) -> str:
        data = [
            {
                "id": alert.id,
                "rule_id": alert.rule_id,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "severity": alert.severity,
                "details": alert.details,
            }
            for alert in alerts
        ]
        return json.dumps(data, indent=2, default=str)

    def get_mime_type(self) -> str:
        return "application/json"

    def get_extension(self) -> str:
        return ".json"


class CsvExporter(BaseExporter):
    """CSV export formatter."""

    def export_logs(self, logs: list[LogEntry]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "timestamp", "level", "message", "service", "host", "trace_id", "span_id", "created_at"])
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat() if log.timestamp else "",
                log.level,
                log.message,
                log.service or "",
                log.host or "",
                log.trace_id or "",
                log.span_id or "",
                log.created_at.isoformat() if log.created_at else "",
            ])
        return output.getvalue()

    def export_alerts(self, alerts: list[AlertHistory]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "rule_id", "triggered_at", "resolved_at", "severity", "details"])
        for alert in alerts:
            writer.writerow([
                alert.id,
                alert.rule_id,
                alert.triggered_at.isoformat() if alert.triggered_at else "",
                alert.resolved_at.isoformat() if alert.resolved_at else "",
                alert.severity,
                json.dumps(alert.details) if alert.details else "",
            ])
        return output.getvalue()

    def get_mime_type(self) -> str:
        return "text/csv"

    def get_extension(self) -> str:
        return ".csv"


class HtmlExporter(BaseExporter):
    """HTML export formatter with basic styling."""

    def export_logs(self, logs: list[LogEntry]) -> str:
        rows = ""
        for log in logs:
            rows += f"""<tr>
                <td>{log.id}</td>
                <td>{log.timestamp.isoformat() if log.timestamp else "N/A"}</td>
                <td><span class="badge {log.level.lower()}">{log.level}</span></td>
                <td>{log.message}</td>
                <td>{log.service or "N/A"}</td>
                <td>{log.host or "N/A"}</td>
                <td>{log.trace_id or "N/A"}</td>
            </tr>\n"""
        return self._wrap_html("Log Export", ["ID", "Timestamp", "Level", "Message", "Service", "Host", "Trace ID"], rows)

    def export_alerts(self, alerts: list[AlertHistory]) -> str:
        rows = ""
        for alert in alerts:
            rows += f"""<tr>
                <td>{alert.id}</td>
                <td>{alert.rule_id}</td>
                <td>{alert.triggered_at.isoformat() if alert.triggered_at else "N/A"}</td>
                <td>{alert.resolved_at.isoformat() if alert.resolved_at else "N/A"}</td>
                <td><span class="badge {alert.severity.lower()}">{alert.severity}</span></td>
                <td><pre>{json.dumps(alert.details, indent=2) if alert.details else "N/A"}</pre></td>
            </tr>\n"""
        return self._wrap_html("Alert History Export", ["ID", "Rule ID", "Triggered At", "Resolved At", "Severity", "Details"], rows)

    def _wrap_html(self, title: str, headers: list[str], rows: str) -> str:
        header_cells = "".join(f"<th>{h}</th>" for h in headers)
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1400px; margin: 40px auto; padding: 20px; background: #f8f9fa; }}
h1 {{ color: #212529; border-bottom: 2px solid #0d6efd; padding-bottom: 12px; }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #dee2e6; }}
th {{ background: #0d6efd; color: white; font-weight: 600; }}
tr:hover {{ background: #f1f3f5; }}
.badge {{ padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
.badge.debug {{ background: #e9ecef; color: #495057; }}
.badge.info {{ background: #e7f3ff; color: #0d6efd; }}
.badge.warning {{ background: #fff3cd; color: #856404; }}
.badge.error {{ background: #f8d7da; color: #721c24; }}
.badge.critical {{ background: #f5c6cb; color: #721c24; }}
pre {{ margin: 0; font-size: 12px; background: #f8f9fa; padding: 8px; border-radius: 4px; }}
.meta {{ color: #6c757d; font-size: 14px; margin-bottom: 20px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">Generated: {datetime.now().isoformat()} | Total Records: {rows.count('<tr>')}</p>
<table>
<thead><tr>{header_cells}</tr></thead>
<tbody>{rows}</tbody>
</table>
</body>
</html>"""

    def get_mime_type(self) -> str:
        return "text/html"

    def get_extension(self) -> str:
        return ".html"


class ExportRegistry:
    """Factory for getting exporters by format name."""

    _exporters: dict[str, type[BaseExporter]] = {
        "json": JsonExporter,
        "csv": CsvExporter,
        "html": HtmlExporter,
    }

    @classmethod
    def get_exporter(cls, name: str) -> BaseExporter:
        exporter_class = cls._exporters.get(name.lower())
        if not exporter_class:
            available = ", ".join(cls._exporters.keys())
            raise ValueError(f"Unknown format '{name}'. Available: {available}")
        return exporter_class()

    @classmethod
    def list_formats(cls) -> list[str]:
        return list(cls._exporters.keys())


def query_logs_for_export(
    db: Session,
    user_id: str,
    level: str | None = None,
    service: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 1000,
) -> list[LogEntry]:
    """
    Query log entries for export, optionally filtered.
    """
    query = db.query(LogEntry)

    if level:
        query = query.filter(LogEntry.level == level.upper())
    if service:
        query = query.filter(LogEntry.service == service)
    if start_date:
        query = query.filter(LogEntry.timestamp >= start_date)
    if end_date:
        query = query.filter(LogEntry.timestamp <= end_date)

    return query.order_by(LogEntry.created_at.desc()).limit(limit).all()


def query_alerts_for_export(
    db: Session,
    user_id: str,
    rule_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 1000,
) -> list[AlertHistory]:
    """
    Query alert history for export, optionally filtered.
    """
    # Get user's rule IDs
    user_rule_ids = db.query(AlertRule.id).filter(AlertRule.user_id == user_id).subquery()

    query = db.query(AlertHistory).filter(AlertHistory.rule_id.in_(user_rule_ids))

    if rule_id:
        query = query.filter(AlertHistory.rule_id == rule_id)
    if start_date:
        query = query.filter(AlertHistory.triggered_at >= start_date)
    if end_date:
        query = query.filter(AlertHistory.triggered_at <= end_date)

    return query.order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
