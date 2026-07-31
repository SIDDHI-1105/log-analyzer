"""
backend/tests/conftest.py

Pytest fixtures for backend API tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

# CRITICAL: Ensure backend/src is at the FRONT of sys.path before any imports
_backend_src = str(Path(__file__).parent.parent / "src")
if _backend_src in sys.path:
    sys.path.remove(_backend_src)
sys.path.insert(0, _backend_src)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, get_db
from main import app
from core.security import get_password_hash, create_access_token
from models.user import User

# Import all models so they register with Base.metadata
from models import User as _U, AlertRule, AlertHistory, Dashboard, ApiKey, LogEntry  # noqa: F401

# Use SQLite in-memory for fast tests
TEST_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override the database dependency with a test session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency BEFORE creating TestClient
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Drops and recreates all tables before each test.
    """
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Return a TestClient with the test database."""
    yield TestClient(app)


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user and return it."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        role="viewer",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Return authorization headers for the test user."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}
