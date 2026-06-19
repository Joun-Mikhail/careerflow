"""Schemas for users and authentication."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.base import IdentifiedModel

# bcrypt hashes at most 72 bytes; cap here so validation is explicit and the
# security layer never has to truncate silently.
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 72


class UserCreate(BaseModel):
    """Registration payload."""

    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    full_name: str | None = Field(default=None, max_length=120)


class UserLogin(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class UserRead(IdentifiedModel):
    """Public representation of a user (never includes the password hash)."""

    email: EmailStr
    full_name: str | None
    is_active: bool


class Token(BaseModel):
    """Issued access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token lifetime in seconds.")


class AuthResponse(BaseModel):
    """Returned by register/login: the user plus their access token."""

    model_config = ConfigDict(from_attributes=True)

    user: UserRead
    token: Token
