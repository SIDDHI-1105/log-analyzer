"""
backend/src/schemas/user.py

Pydantic schemas for user authentication and profile.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields shared across schemas."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration (request body)."""
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(UserBase):
    """Schema for user login (request body)."""
    password: str


class UserResponse(UserBase):
    """Schema for user profile (response)."""
    id: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT payload."""
    sub: str | None = None  # user id