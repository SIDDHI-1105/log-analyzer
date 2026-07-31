"""
backend/tests/test_auth.py

Tests for authentication endpoints.
"""

from __future__ import annotations


def test_register_success(client):
    """Test user registration with valid credentials."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user):
    """Test registration with an already existing email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "securepassword123",
        },
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, test_user):
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with a user that doesn't exist."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "somepassword",
        },
    )
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers, test_user):
    """Test getting current user profile with valid token."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id
    assert data["role"] == test_user.role
    assert data["is_active"] == test_user.is_active


def test_get_me_unauthenticated(client):
    """Test getting profile without authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    """Test getting profile with an invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401
