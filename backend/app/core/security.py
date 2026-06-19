"""Password hashing and JWT token primitives.

This module is intentionally free of any web-framework or database imports so
it can be unit-tested in isolation. Password hashing uses bcrypt directly;
tokens are signed with PyJWT using the configured secret and algorithm.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.errors import AuthenticationError

settings = get_settings()

# bcrypt operates on at most 72 bytes; inputs are validated to this length at
# the schema layer, but we guard here too so hashing never silently truncates.
_BCRYPT_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Return a salted bcrypt hash for ``plain_password``."""
    password_bytes = _encode_password(plain_password)
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` when ``plain_password`` matches the stored hash."""
    try:
        return bcrypt.checkpw(_encode_password(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed stored hash — treat as a non-match rather than crashing.
        return False


def _encode_password(plain_password: str) -> bytes:
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > _BCRYPT_MAX_BYTES:
        raise AuthenticationError("Password exceeds the maximum supported length.")
    return password_bytes


def create_access_token(subject: UUID | str, *, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token for ``subject`` (the user id)."""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": str(subject), "iat": now, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID:
    """Validate ``token`` and return the subject (user id).

    Raises :class:`AuthenticationError` for any invalid, expired, or malformed
    token so the caller can respond with ``401`` uniformly.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Could not validate credentials.") from exc

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Could not validate credentials.")
    try:
        return UUID(str(subject))
    except ValueError as exc:
        raise AuthenticationError("Could not validate credentials.") from exc
