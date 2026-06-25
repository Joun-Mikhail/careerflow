"""Schemas for certificate resources."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, computed_field

from app.schemas.base import IdentifiedModel


class CertificateUpdate(BaseModel):
    """Payload for editing certificate metadata."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    issuer: str | None = Field(default=None, max_length=200)
    issued_on: date | None = None
    credential_url: str | None = Field(default=None, max_length=500)


class CertificateRead(IdentifiedModel):
    """Certificate representation returned by the API."""

    name: str
    issuer: str | None
    issued_on: date | None
    credential_url: str | None
    original_filename: str | None
    content_type: str | None
    size_bytes: int | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_file(self) -> bool:
        return self.original_filename is not None
