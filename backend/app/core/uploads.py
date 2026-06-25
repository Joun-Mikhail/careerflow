"""Shared validation for uploaded document bytes."""

from __future__ import annotations

from collections.abc import Mapping

from app.core.config import get_settings
from app.core.errors import ValidationError

settings = get_settings()

# Content types accepted for CVs.
CV_CONTENT_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

# Certificates additionally allow common image scans.
CERTIFICATE_CONTENT_TYPES: dict[str, str] = {
    **CV_CONTENT_TYPES,
    "image/png": ".png",
    "image/jpeg": ".jpg",
}


def validate_upload(content: bytes, content_type: str, allowed: Mapping[str, str]) -> str:
    """Validate uploaded bytes against an allow-list; return the file suffix.

    Raises :class:`ValidationError` for an unsupported type, an empty file, or
    a file exceeding the configured maximum size.
    """
    if content_type not in allowed:
        raise ValidationError(
            "Unsupported file type.",
            details={"allowed": sorted(allowed)},
        )
    if not content:
        raise ValidationError("Uploaded file is empty.")
    if len(content) > settings.max_upload_size_bytes:
        raise ValidationError(
            "File exceeds the maximum allowed size.",
            details={"max_bytes": settings.max_upload_size_bytes},
        )
    return allowed[content_type]
