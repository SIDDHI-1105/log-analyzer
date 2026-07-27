"""backend/src/core/database.py

SQLAlchemy database setup.

Provides:
- Engine: Connection pool to PostgreSQL
- SessionLocal: Factory for database sessions
- Base: Declarative base for all models
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import get_settings

settings = get_settings()

# Create engine with connection pooling
engine = create_engine(
    settings.database_url_str,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,        # Number of connections to keep open
    max_overflow=20,     # Extra connections allowed during spikes
    echo=settings.DEBUG, # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes.

    Yields a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
