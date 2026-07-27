"""
cli.py

Command-line interface for the Log Analyzer.

This is the main entry point users interact with. It orchestrates:
    1. Parse command-line arguments
    2. Select the right parser (auto-detect or user-specified)
    3. Parse the log file
    4. Analyze the results
    5. Generate the report in the requested format
    6. Save or print the output

Design principles:
- Clear, helpful error messages
- Sensible defaults (auto-detect format, console output)
- Progress feedback for large files
- Exit codes (0 = success, 1 = error, 2 = bad arguments)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from src.analyzer import LogAnalyzer
from src.models import AlertRule, LogLevel
from src.parsers import ParserRegistry
from src.reporters import ReporterRegistry


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser.

    We use argparse (standard library) because:
    - No external dependency needed
    - Auto-generates --help
    - Built-in type validation
    - Supports subcommands (future-proof)
    """
    parser = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze log files and generate insightful reports.",
        epilog="Example: python -m src.cli app.log --format json --output report.json",
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to the log file to analyze",
    )

    parser.add_argument(
        "--format",
        "-f",
        type=str,
        default="console",
        choices=ReporterRegistry.list_reporters(),
        help="Output format (default: console)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path (default: print to stdout)",
    )

    parser.add_argument(
        "--parser",
        "-p",
        type=str,
        default="auto",
        choices=["auto"] + ParserRegistry.list_parsers(),
        help="Log parser to use (default: auto-detect)",
    )

    parser.add_argument(
        "--alert-severity",
        type=str,
        default=None,
        choices=[l.value for l in LogLevel],
        help="Minimum severity to trigger alerts",
    )

    parser.add_argument(
        "--alert-threshold",
        type=int,
        default=5,
        help="Alert threshold count (default: 5)",
    )

    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top messages/services to show (default: 10)",
    )

    return parser


def validate_file_path(path: str) -> Path:
    """
    Validate that the file exists and is readable.

    Uses os.access() because pathlib.Path does NOT have a .readable() method.
    os.access(path, os.R_OK) checks if the current user has read permission.
    """
    file_path = Path(path)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not file_path.is_file():
        print(f"Error: Not a file: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not os.access(file_path, os.R_OK):
        print(f"Error: Cannot read file (permission denied): {file_path}", file=sys.stderr)
        sys.exit(1)

    return file_path


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        0 on success, 1 on processing error, 2 on argument error.
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validate input file
    file_path = validate_file_path(args.file)

    # Select parser
    if args.parser == "auto":
        # Read first non-empty line to detect format
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            sample = ""
            for line in f:
                sample = line.strip()
                if sample:
                    break

        selected_parser = ParserRegistry.auto_detect(sample)
        if not selected_parser:
            print("Error: Could not auto-detect log format.", file=sys.stderr)
            print("Try specifying --parser manually.", file=sys.stderr)
            sys.exit(1)
        parser_name = type(selected_parser).__name__
    else:
        selected_parser = ParserRegistry.get_parser(args.parser)
        parser_name = args.parser

    print(f"Using parser: {parser_name}")
    print(f"Analyzing: {file_path}")
    print()

    # Parse the file
    try:
        batch = selected_parser.parse_file(file_path)
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {batch.total_lines_read} lines ({batch.success_rate}% success)")
    print(f"Extracted {len(batch.entries)} valid entries")
    print()

    # Analyze
    analyzer = LogAnalyzer(batch)
    result = analyzer.analyze()

    # Evaluate alerts if requested
    if args.alert_severity:
        rule = AlertRule(
            name=f"{args.alert_severity} Alert",
            severity=LogLevel(args.alert_severity),
            threshold=args.alert_threshold,
        )
        triggered = analyzer.evaluate_alerts([rule])
        result.alerts_triggered = triggered

    # Generate report
    reporter = ReporterRegistry.get_reporter(args.format)
    report = reporter.generate(result, batch)

    # Output
    if args.output:
        output_path = Path(args.output)
        try:
            output_path.write_text(report, encoding="utf-8")
            print(f"Report saved to: {output_path}")
        except Exception as e:
            print(f"Error saving report: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())