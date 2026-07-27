"""
parsers.py

Extensible log parsing engine using the Strategy Pattern.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.models import LogBatch, LogEntry, LogLevel


class BaseParser(ABC):
    """Abstract base class for all log parsers."""

    @abstractmethod
    def parse_line(self, raw_line: str) -> LogEntry | None:
        """Parse a single raw log line into a structured LogEntry."""
        ...

    @abstractmethod
    def can_parse(self, raw_line: str) -> bool:
        """Check if this parser can handle the given line."""
        ...

    def parse_file(self, file_path: str | Path) -> LogBatch:
        """Parse an entire file and return a LogBatch with statistics."""
        path = Path(file_path)
        batch = LogBatch(source=str(path))

        with path.open("r", encoding="utf-8", errors="replace") as file:
            for line in file:
                raw = line.rstrip("\n\r")
                if not raw.strip():
                    batch.record_success()
                    continue

                entry = self.parse_line(raw)
                if entry:
                    batch.add_entry(entry)
                    batch.record_success()
                else:
                    batch.record_failure()

        return batch


class PlainTextParser(BaseParser):
    """Parser for standard plain-text log files."""

    PATTERNS = [
        re.compile(
            r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
            r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\s+"
            r"(?P<message>.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\[(?P<timestamp>[^\]]+)\]\s+"
            r"(?:\[(?P<service>[^\]]+)\]\s+)?"
            r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\s+"
            r"(?P<message>.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL):\s*"
            r"(?P<message>.+)$",
            re.IGNORECASE,
        ),
        re.compile(r"^(?P<message>.+)$"),
    ]

    def can_parse(self, raw_line: str) -> bool:
        for pattern in self.PATTERNS:
            if pattern.match(raw_line):
                return True
        return False

    def parse_line(self, raw_line: str) -> LogEntry | None:
        # Skip empty or whitespace-only lines
        if not raw_line.strip():
            return None

        for pattern in self.PATTERNS:
            match = pattern.match(raw_line)
            if match:
                groups = match.groupdict()
                message = groups.get("message", raw_line).strip()
                # Double-check message isn't empty after extraction
                if not message:
                    return None
                return LogEntry(
                    timestamp=groups.get("timestamp"),
                    level=groups.get("level", "INFO").upper(),
                    message=message,
                    service=groups.get("service"),
                    raw_line=raw_line,
                )
        return None


class JsonParser(BaseParser):
    """Parser for structured JSON logs."""

    def can_parse(self, raw_line: str) -> bool:
        raw_line = raw_line.strip()
        if not raw_line.startswith("{"):
            return False
        try:
            json.loads(raw_line)
            return True
        except json.JSONDecodeError:
            return False

    def parse_line(self, raw_line: str) -> LogEntry | None:
        try:
            data = json.loads(raw_line.strip())
        except json.JSONDecodeError:
            return None

        timestamp = (
            data.get("timestamp")
            or data.get("time")
            or data.get("@timestamp")
            or data.get("ts")
        )
        level = (
            data.get("level")
            or data.get("severity")
            or data.get("log_level")
            or "INFO"
        )
        message = data.get("message") or data.get("msg") or data.get("log") or ""
        service = (
            data.get("service")
            or data.get("app")
            or data.get("application")
            or data.get("logger")
        )
        host = data.get("host") or data.get("hostname") or data.get("source")
        trace_id = data.get("trace_id") or data.get("traceId") or data.get("trace")
        span_id = data.get("span_id") or data.get("spanId") or data.get("span")

        known_keys = {
            "timestamp", "time", "@timestamp", "ts",
            "level", "severity", "log_level",
            "message", "msg", "log",
            "service", "app", "application", "logger",
            "host", "hostname", "source",
            "trace_id", "traceId", "trace",
            "span_id", "spanId", "span",
        }
        metadata = {k: v for k, v in data.items() if k not in known_keys}

        return LogEntry(
            timestamp=timestamp,
            level=level.upper(),
            message=str(message),
            service=service,
            host=host,
            trace_id=trace_id,
            span_id=span_id,
            metadata=metadata,
            raw_line=raw_line,
        )


class NginxParser(BaseParser):
    """Parser for Nginx access logs."""

    PATTERN = re.compile(
        r'^(?P<remote_addr>\S+)\s+'
        r'(?P<remote_user>\S+)\s+'
        r'(?P<remote_user2>\S+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+'
        r'(?P<status>\d{3})\s+'
        r'(?P<body_bytes_sent>\d+)\s+'
        r'"(?P<referrer>[^"]*)"\s+'
        r'"(?P<user_agent>[^"]*)"'
    )

    def can_parse(self, raw_line: str) -> bool:
        return self.PATTERN.match(raw_line) is not None

    def parse_line(self, raw_line: str) -> LogEntry | None:
        match = self.PATTERN.match(raw_line)
        if not match:
            return None

        groups = match.groupdict()
        status = int(groups["status"])

        if status >= 500:
            level = LogLevel.ERROR
        elif status >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO

        message = (
            f"{groups['method']} {groups['path']} -> {status} "
            f"({groups['body_bytes_sent']} bytes)"
        )

        return LogEntry(
            timestamp=groups["timestamp"],
            level=level,
            message=message,
            host=groups["remote_addr"],
            metadata={
                "method": groups["method"],
                "path": groups["path"],
                "protocol": groups["protocol"],
                "status": status,
                "body_bytes_sent": int(groups["body_bytes_sent"]),
                "referrer": groups["referrer"],
                "user_agent": groups["user_agent"],
            },
            raw_line=raw_line,
        )


class ParserRegistry:
    """Factory for getting the right parser."""

    _parsers: dict[str, type[BaseParser]] = {
        "plaintext": PlainTextParser,
        "json": JsonParser,
        "nginx": NginxParser,
    }

    @classmethod
    def get_parser(cls, name: str) -> BaseParser:
        parser_class = cls._parsers.get(name.lower())
        if not parser_class:
            available = ", ".join(cls._parsers.keys())
            raise ValueError(f"Unknown parser '{name}'. Available: {available}")
        return parser_class()

    @classmethod
    def register(cls, name: str, parser_class: type[BaseParser]) -> None:
        cls._parsers[name.lower()] = parser_class

    @classmethod
    def auto_detect(cls, sample_line: str) -> BaseParser | None:
        """
        Try all parsers and return the first one that can parse the line.

        Order matters: we check structured formats (JSON, Nginx) before
        catch-all formats (PlainText) to avoid false positives.
        """
        # Check structured formats first to avoid false matches
        structured_parsers = ["json", "nginx"]
        for name in structured_parsers:
            if name in cls._parsers:
                parser = cls._parsers[name]()
                if parser.can_parse(sample_line):
                    return parser

        # Then check catch-all formats
        for name, parser_class in cls._parsers.items():
            if name in structured_parsers:
                continue
            parser = parser_class()
            if parser.can_parse(sample_line):
                return parser

        return None

    @classmethod
    def list_parsers(cls) -> list[str]:
        return list(cls._parsers.keys())