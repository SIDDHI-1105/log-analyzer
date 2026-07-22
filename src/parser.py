"""
parser.py

This module is responsible for reading log files.
"""


def read_log_file(file_path: str) -> list[str]:
    """
    Reads a log file and returns all lines.

    Args:
        file_path (str): Path to the log file.

    Returns:
        list[str]: List of log lines.
    """

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        return lines

    except FileNotFoundError:
        raise FileNotFoundError(f"Log file not found: {file_path}")

    except PermissionError:
        raise PermissionError(f"Permission denied: {file_path}")