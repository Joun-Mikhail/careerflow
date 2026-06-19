"""Schemas for attachment resources (metadata only)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.models.enums import AttachmentKind
from app.schemas.base import ORMModel


class AttachmentRead(ORMModel):
    """Metadata describing an uploaded attachment."""

    id: UUID
    application_id: UUID
    kind: AttachmentKind
    original_filename: str
    content_type: str
    size_bytes: int


class AttachmentList(BaseModel):
    """Container for an application's attachment metadata."""

    items: list[AttachmentRead]
