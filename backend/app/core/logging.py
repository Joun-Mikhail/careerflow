"""Structured logging configuration.

Logs are emitted as single-line key=value records that are easy to read in
development and straightforward to ingest in production. No secrets, tokens, or
full PII should ever be passed to the logger.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

_CONFIGURED = False

#: Dedicated logger for structured audit events of security-relevant actions.
_audit_logger = logging.getLogger("careerflow.audit")


def configure_logging(*, debug: bool = False) -> None:
    """Configure root logging once for the process."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s level=%(levelname)s logger=%(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Uvicorn access logs are noisy at INFO during tests; keep them at WARNING.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)


def log_action(
    action: str,
    *,
    status: str,
    user_id: UUID | str | None = None,
    **extra: Any,
) -> None:
    """Emit a structured JSON audit record for a security-relevant action.

    Every record carries a timestamp, the action, the acting user id (when
    known), and an outcome status. No secrets or PII beyond the user id are
    included.
    """
    payload: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "user_id": str(user_id) if user_id is not None else None,
        "status": status,
        **extra,
    }
    _audit_logger.info(json.dumps(payload))
