"""
backend/tests/test_logs.py

Tests for log endpoints.
"""

from __future__ import annotations


def test_ingest_logs_authenticated(client, auth_headers):
    """Test log ingestion with valid authentication."""
    response = client.post(
        "/api/v1/logs/ingest",
        headers=auth_headers,
        json={
            "entries": [
                {
                    "level": "INFO",
                    "message": "Test log message",
                    "service": "test-service",
                    "host": "localhost",
                }
            ]
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ingested"] == 1
    assert data["failed"] == 0


def test_ingest_logs_unauthenticated(client):
    """Test log ingestion without authentication."""
    response = client.post(
        "/api/v1/logs/ingest",
        json={
            "entries": [
                {
                    "level": "INFO",
                    "message": "Test log message",
                }
            ]
        },
    )
    assert response.status_code == 401


def test_list_logs_authenticated(client, auth_headers):
    """Test listing logs with authentication."""
    # First ingest some logs
    client.post(
        "/api/v1/logs/ingest",
        headers=auth_headers,
        json={
            "entries": [
                {"level": "INFO", "message": "Log 1", "service": "svc1"},
                {"level": "ERROR", "message": "Log 2", "service": "svc2"},
            ]
        },
    )

    # Then list them
    response = client.get("/api/v1/logs/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    messages = {log["message"] for log in data}
    assert messages == {"Log 1", "Log 2"}


def test_list_logs_with_level_filter(client, auth_headers):
    """Test listing logs with level filter."""
    # Ingest logs with different levels
    client.post(
        "/api/v1/logs/ingest",
        headers=auth_headers,
        json={
            "entries": [
                {"level": "INFO", "message": "Info log"},
                {"level": "ERROR", "message": "Error log"},
            ]
        },
    )

    # Filter by ERROR level
    response = client.get("/api/v1/logs/?level=ERROR", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["level"] == "ERROR"
    assert data[0]["message"] == "Error log"


def test_list_logs_unauthenticated(client):
    """Test listing logs without authentication."""
    response = client.get("/api/v1/logs/")
    assert response.status_code == 401


def test_list_logs_pagination(client, auth_headers):
    """Test log pagination."""
    # Ingest multiple logs
    entries = [{"level": "INFO", "message": f"Log {i}"} for i in range(5)]
    client.post(
        "/api/v1/logs/ingest",
        headers=auth_headers,
        json={"entries": entries},
    )

    # Test skip and limit
    response = client.get("/api/v1/logs/?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    response = client.get("/api/v1/logs/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
