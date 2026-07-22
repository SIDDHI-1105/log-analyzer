import pytest

from src.parser import read_log_file


def test_read_log_file():
    logs = read_log_file("sample_logs/app.log")

    assert len(logs) == 7


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_log_file("sample_logs/not_found.log")