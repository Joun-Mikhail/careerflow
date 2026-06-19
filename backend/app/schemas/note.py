"""Schemas for note resources."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import IdentifiedModel


class NoteCreate(BaseModel):
    """Payload for creating a note (Markdown body)."""

    body: str = Field(min_length=1, max_length=50_000)


class NoteUpdate(BaseModel):
    """Payload for updating a note."""

    body: str = Field(min_length=1, max_length=50_000)


class NoteRead(IdentifiedModel):
    """Note representation returned by the API."""

    application_id: UUID
    body: str
