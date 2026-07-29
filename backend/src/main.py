"""
backend/src/main.py

FastAPI application entry point.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import auth as auth_v1
from api.v1 import logs as logs_v1
from api.v1 import alerts as alerts_v1
from api.v1 import dashboards as dashboards_v1
from api.v1 import export as export_v1
from api.v1 import api_keys as api_keys_v1
from api.v1 import live_tail as live_tail_v1
from core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routers
app.include_router(auth_v1.router, prefix="/api/v1")
app.include_router(logs_v1.router, prefix="/api/v1")
app.include_router(alerts_v1.router, prefix="/api/v1")
app.include_router(dashboards_v1.router, prefix="/api/v1")
app.include_router(export_v1.router, prefix="/api/v1")
app.include_router(api_keys_v1.router, prefix="/api/v1")
app.include_router(live_tail_v1.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """
    Public health check endpoint.
    """
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }


@app.get("/api/v1/health", tags=["Health"])
def api_health_check() -> dict[str, str]:
    """
    Versioned health check endpoint.
    """
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }
