"""
test_cli.py

Tests for the command-line interface.

Uses pytest's monkeypatch and capsys fixtures to test CLI behavior
without actually running subprocesses.
"""

import sys
from pathlib import Path

import pytest

from src.cli import create_argument_parser, main, validate_file_path


class TestArgumentParser:
    """Tests for CLI argument parsing."""

    def test_parser_accepts_file_argument(self):
        """Should require a file path."""
        parser = create_argument_parser()
        args = parser.parse_args(["myapp.log"])
        assert args.file == "myapp.log"

    def test_default_format_is_console(self):
        """Default output format should be console."""
        parser = create_argument_parser()
        args = parser.parse_args(["app.log"])
        assert args.format == "console"

    def test_format_choices(self):
        """Should accept valid format choices."""
        parser = create_argument_parser()
        for fmt in ["json", "csv", "html", "console"]:
            args = parser.parse_args(["app.log", "--format", fmt])
            assert args.format == fmt

    def test_parser_rejects_invalid_format(self):
        """Should exit on invalid format."""
        parser = create_argument_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["app.log", "--format", "pdf"])


class TestFileValidation:
    """Tests for file path validation."""

    def test_valid_file(self, tmp_path):
        """Should return Path for existing file."""
        test_file = tmp_path / "test.log"
        test_file.write_text("INFO test")
        result = validate_file_path(str(test_file))
        assert isinstance(result, Path)
        assert result.exists()

    def test_missing_file(self, capsys):
        """Should exit with error for missing file."""
        with pytest.raises(SystemExit) as exc:
            validate_file_path("/nonexistent/path/file.log")
        assert exc.value.code == 1

    def test_directory_not_file(self, tmp_path):
        """Should exit with error if path is a directory."""
        with pytest.raises(SystemExit) as exc:
            validate_file_path(str(tmp_path))
        assert exc.value.code == 1


class TestMainFunction:
    """Integration tests for the main CLI flow."""

    def test_analyzes_sample_log(self, tmp_path, capsys, monkeypatch):
        """End-to-end: create log, run CLI, verify output."""
        log_file = tmp_path / "app.log"
        log_file.write_text(
            "2026-07-26 14:30:00 INFO User login\n"
            "2026-07-26 14:31:00 ERROR Database fail\n"
        )

        monkeypatch.setattr(sys, "argv", ["cli", str(log_file)])
        exit_code = main()
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "PlainTextParser" in captured.out
        assert "LOG ANALYSIS REPORT" in captured.out
        assert "ERROR" in captured.out

    def test_json_output(self, tmp_path, capsys, monkeypatch):
        """Should produce valid JSON when requested."""
        log_file = tmp_path / "app.log"
        log_file.write_text("2026-07-26 14:30:00 INFO test\n")

        monkeypatch.setattr(
            sys, "argv", ["cli", str(log_file), "--format", "json"]
        )
        main()
        captured = capsys.readouterr()
        assert '"total_entries"' in captured.out

    def test_output_to_file(self, tmp_path, monkeypatch):
        """Should save report to specified file."""
        log_file = tmp_path / "app.log"
        log_file.write_text("2026-07-26 14:30:00 INFO test\n")
        output_file = tmp_path / "report.html"

        monkeypatch.setattr(
            sys,
            "argv",
            ["cli", str(log_file), "--format", "html", "--output", str(output_file)],
        )
        main()
        assert output_file.exists()
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content