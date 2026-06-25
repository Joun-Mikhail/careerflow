"""Schemas for CV resources."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from app.models.enums import CvSource
from app.schemas.base import IdentifiedModel


class CvUpdate(BaseModel):
    """Payload for renaming a CV or marking it the default."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    is_default: bool | None = None


class CvRead(IdentifiedModel):
    """CV representation returned by the API (without the full text body)."""

    title: str
    source: CvSource
    is_default: bool
    original_filename: str | None
    content_type: str | None
    size_bytes: int | None
    parent_cv_id: UUID | None
    job_id: UUID | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_file(self) -> bool:
        return self.original_filename is not None


class CvDetail(CvRead):
    """CV representation including the tailored text body, when present."""

    content_text: str | None
