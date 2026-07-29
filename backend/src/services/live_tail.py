"""
backend/src/services/live_tail.py

In-memory pub/sub for live log tailing via WebSockets.

This is a simple broadcast mechanism. When logs are ingested,
they are pushed to all connected WebSocket clients that match
the filter criteria.

For production with multiple server instances, replace this with
Redis pub/sub or a message broker.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket


class LiveTailManager:
    """
    Manages WebSocket connections for live log tailing.

    Each connection can specify filters (level, service).
    When a new log is ingested, it's broadcast to all matching connections.
    """

    def __init__(self) -> None:
        self.connections: list[dict[str, Any]] = []

    async def connect(
        self,
        websocket: WebSocket,
        level_filter: str | None = None,
        service_filter: str | None = None,
    ) -> None:
        """
        Accept a WebSocket connection and register it.
        """
        await websocket.accept()
        self.connections.append({
            "websocket": websocket,
            "level_filter": level_filter.upper() if level_filter else None,
            "service_filter": service_filter,
        })

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.
        """
        self.connections = [
            conn for conn in self.connections
            if conn["websocket"] != websocket
        ]

    async def broadcast_log(self, log_data: dict[str, Any]) -> None:
        """
        Broadcast a log entry to all matching WebSocket connections.

        A connection receives the log if:
        - No level filter is set, OR the log level matches
        - No service filter is set, OR the log service matches
        """
        dead_connections: list[WebSocket] = []

        for conn in self.connections:
            ws = conn["websocket"]
            level_filter = conn["level_filter"]
            service_filter = conn["service_filter"]

            # Check filters
            if level_filter and log_data.get("level", "").upper() != level_filter:
                continue
            if service_filter and log_data.get("service") != service_filter:
                continue

            try:
                await ws.send_json(log_data)
            except Exception:
                # Connection is dead, mark for cleanup
                dead_connections.append(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(ws)


# Global singleton instance
live_tail_manager = LiveTailManager()
