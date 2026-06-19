"""Schemas for company resources."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.base import IdentifiedModel


class CompanyBase(BaseModel):
    """Fields common to create and update payloads."""

    name: str = Field(min_length=1, max_length=200)
    website: str | None = Field(default=None, max_length=500)
    industry: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=10_000)


class CompanyCreate(CompanyBase):
    """Payload for creating a company."""


class CompanyUpdate(BaseModel):
    """Payload for partially updating a company (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    website: str | None = Field(default=None, max_length=500)
    industry: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=10_000)


class CompanyRead(IdentifiedModel):
    """Company representation returned by the API."""

    name: str
    website: str | None
    industry: str | None
    location: str | None
    notes: str | None
