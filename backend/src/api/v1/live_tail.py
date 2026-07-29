"""
backend/src/api/v1/live_tail.py

WebSocket endpoint for live log tailing.

Clients connect via WebSocket and receive real-time log entries
as they are ingested into the system.

Authentication: JWT token passed as query parameter `token`.
"""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from core.config import get_settings
from services.live_tail import live_tail_manager

router = APIRouter(prefix="/live-tail", tags=["Live Tail"])

settings = get_settings()


def _safe_decode_token(token: str) -> str | None:
    """
    Safely decode a JWT token without raising HTTPException.

    Returns the user_id if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except (JWTError, Exception):
        return None


@router.websocket("/")
async def live_tail_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token for authentication"),
    level: str | None = Query(default=None, description="Filter by log level"),
    service: str | None = Query(default=None, description="Filter by service name"),
) -> None:
    """
    WebSocket endpoint for live log tailing.

    Connect with: ws://localhost:8000/api/v1/live-tail/?token=YOUR_JWT_TOKEN

    Optional query params:
    - level: Filter to only show logs of this level (e.g., ERROR)
    - service: Filter to only show logs from this service (e.g., api)

    The server will push new log entries as JSON objects in real-time.
    """
    # Authenticate the token safely (no HTTPException in WebSocket context)
    user_id = _safe_decode_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # Register connection with filters
    await live_tail_manager.connect(websocket, level_filter=level, service_filter=service)

    try:
        # Keep the connection alive, handle client pings if needed
        while True:
            # Wait for any message from client (ping/heartbeat)
            data = await websocket.receive_text()
            # Echo back as heartbeat acknowledgment
            await websocket.send_json({"type": "heartbeat", "status": "connected"})
    except WebSocketDisconnect:
        live_tail_manager.disconnect(websocket)
    except Exception:
        live_tail_manager.disconnect(websocket)
