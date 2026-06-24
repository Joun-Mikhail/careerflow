"""Rate limiting for sensitive endpoints.

A single shared :class:`Limiter` keyed by client IP, with rate-limit headers
enabled. It is disabled under the ``test`` profile so the broad test suite
(which logs in many times) does not trip limits; the dedicated rate-limit test
re-enables it explicitly.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

#: Limit applied to authentication endpoints (login, refresh, change-password).
AUTH_RATE_LIMIT = "10/minute"

limiter = Limiter(
    key_func=get_remote_address,
    headers_enabled=True,
    enabled=settings.environment != "test",
)
