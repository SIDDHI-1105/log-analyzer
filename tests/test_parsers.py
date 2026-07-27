"""
test_parsers.py

Tests for all log parsers.

Verifies that each parser correctly handles its supported formats
and returns None for lines it cannot parse.
"""

import pytest

from src.models import LogEntry, LogLevel
from src.parsers import (
    JsonParser,
    NginxParser,
    ParserRegistry,
    PlainTextParser,
)


class TestPlainTextParser:
    """Tests for the plain text log parser."""

    def test_standard_format(self):
        """2026-07-26 14:32:15 INFO message"""
        parser = PlainTextParser()
        entry = parser.parse_line("2026-07-26 14:32:15 INFO User logged in")
        assert entry is not None
        assert entry.level == LogLevel.INFO
        assert "User logged in" in entry.message

    def test_bracket_format(self):
        """[2026-07-26 14:32:15] [service] ERROR message"""
        parser = PlainTextParser()
        entry = parser.parse_line(
            "[2026-07-26 14:32:15] [auth-service] ERROR Database timeout"
        )
        assert entry is not None
        assert entry.service == "auth-service"
        assert entry.level == LogLevel.ERROR

    def test_level_only_format(self):
        """ERROR: message"""
        parser = PlainTextParser()
        entry = parser.parse_line("ERROR: Something broke")
        assert entry is not None
        assert entry.level == LogLevel.ERROR

    def test_message_only(self):
        """Lines with no level or timestamp."""
        parser = PlainTextParser()
        entry = parser.parse_line("Just a plain message")
        assert entry is not None
        assert entry.level == LogLevel.INFO  # Default
        assert entry.message == "Just a plain message"

    def test_empty_line_returns_none(self):
        """Empty lines should not parse."""
        parser = PlainTextParser()
        assert parser.parse_line("") is None
        assert parser.parse_line("   ") is None

    def test_can_parse_detects_valid_lines(self):
        """can_parse should return True for supported formats."""
        parser = PlainTextParser()
        assert parser.can_parse("2026-07-26 14:32:15 INFO test") is True
        assert parser.can_parse("ERROR: test") is True


class TestJsonParser:
    """Tests for the JSON log parser."""

    def test_standard_json(self):
        """Standard structured JSON log."""
        parser = JsonParser()
        line = '{"timestamp":"2026-07-26T14:32:15Z","level":"ERROR","message":"fail","service":"api"}'
        entry = parser.parse_line(line)
        assert entry is not None
        assert entry.level == LogLevel.ERROR
        assert entry.service == "api"
        assert entry.message == "fail"

    def test_json_with_metadata(self):
        """JSON with extra fields should store them in metadata."""
        parser = JsonParser()
        line = '{"level":"INFO","message":"ok","duration_ms":4500,"user_id":123}'
        entry = parser.parse_line(line)
        assert entry is not None
        assert entry.metadata["duration_ms"] == 4500
        assert entry.metadata["user_id"] == 123

    def test_invalid_json_returns_none(self):
        """Malformed JSON should return None, not crash."""
        parser = JsonParser()
        assert parser.parse_line("not json") is None
        assert parser.parse_line("{broken") is None

    def test_can_parse_detects_json(self):
        """can_parse should identify JSON lines."""
        parser = JsonParser()
        assert parser.can_parse('{"level":"INFO"}') is True
        assert parser.can_parse("not json") is False


class TestNginxParser:
    """Tests for the Nginx access log parser."""

    def test_standard_nginx_log(self):
        """Standard combined log format."""
        parser = NginxParser()
        line = '127.0.0.1 - - [26/Jul/2026:14:32:15 +0000] "GET /api/users HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
        entry = parser.parse_line(line)
        assert entry is not None
        assert entry.host == "127.0.0.1"
        assert entry.metadata["method"] == "GET"
        assert entry.metadata["status"] == 200
        assert entry.level == LogLevel.INFO  # 200 -> INFO

    def test_500_error_maps_to_error_level(self):
        """HTTP 500 should map to ERROR level."""
        parser = NginxParser()
        line = '127.0.0.1 - - [26/Jul/2026:14:32:15 +0000] "POST /api/pay HTTP/1.1" 500 128 "-" "curl"'
        entry = parser.parse_line(line)
        assert entry is not None
        assert entry.level == LogLevel.ERROR

    def test_invalid_line_returns_none(self):
        """Non-nginx lines should return None."""
        parser = NginxParser()
        assert parser.parse_line("random text") is None


class TestParserRegistry:
    """Tests for the parser factory."""

    def test_list_parsers(self):
        """Should return all registered parser names."""
        parsers = ParserRegistry.list_parsers()
        assert "plaintext" in parsers
        assert "json" in parsers
        assert "nginx" in parsers

    def test_get_parser(self):
        """Should return an instance of the requested parser."""
        parser = ParserRegistry.get_parser("json")
        assert isinstance(parser, JsonParser)

    def test_get_parser_invalid_name(self):
        """Should raise ValueError for unknown parsers."""
        with pytest.raises(ValueError):
            ParserRegistry.get_parser("unknown")

    def test_auto_detect_plaintext(self):
        """Should detect plain text format."""
        parser = ParserRegistry.auto_detect("2026-07-26 14:32:15 INFO test")
        assert isinstance(parser, PlainTextParser)

    def test_auto_detect_json(self):
        """Should detect JSON format."""
        parser = ParserRegistry.auto_detect('{"level":"ERROR"}')
        assert isinstance(parser, JsonParser)