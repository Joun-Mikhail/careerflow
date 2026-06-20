"""Domain errors and their mapping to HTTP responses.

Services raise these provider-agnostic errors instead of importing FastAPI.
A single set of exception handlers (registered in :mod:`app.main`) converts
them into the consistent error envelope documented in ``docs/04-api-design.md``.
"""

from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


class DomainError(Exception):
    """Base class for expected, recoverable application errors.

    Attributes:
        code: stable machine-readable error code (e.g. ``"not_found"``).
        message: human-readable, safe-to-expose message.
        status_code: HTTP status the API layer should return.
        details: optional structured context (never sensitive).
    """

    code: str = "error"
    status_code: int = 400

    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class PermissionDeniedError(DomainError):
    code = "forbidden"
    status_code = 403


class ConflictError(DomainError):
    code = "conflict"
    status_code = 409


class ValidationError(DomainError):
    code = "validation_error"
    status_code = 422


class AuthenticationError(DomainError):
    code = "unauthorized"
    status_code = 401


def ensure_found(value: T | None, message: str) -> T:
    """Return ``value`` if present, otherwise raise :class:`NotFoundError`.

    Centralizes the "look up an owned entity or 404" pattern used throughout the
    service layer so each service method stays a single expressive line.
    """
    if value is None:
        raise NotFoundError(message)
    return value
