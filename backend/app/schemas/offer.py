"""Schemas for offer resources."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import OfferDecision
from app.schemas.base import IdentifiedModel


class OfferBase(BaseModel):
    """Fields shared by create and update payloads."""

    base_salary: int | None = Field(default=None, ge=0)
    bonus: int | None = Field(default=None, ge=0)
    equity: str | None = Field(default=None, max_length=200)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    benefits: str | None = Field(default=None, max_length=20_000)
    decision: OfferDecision = OfferDecision.PENDING
    received_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=20_000)


class OfferCreate(OfferBase):
    """Payload for creating an offer."""


class OfferUpdate(BaseModel):
    """Payload for partially updating an offer (all fields optional)."""

    base_salary: int | None = Field(default=None, ge=0)
    bonus: int | None = Field(default=None, ge=0)
    equity: str | None = Field(default=None, max_length=200)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    benefits: str | None = Field(default=None, max_length=20_000)
    decision: OfferDecision | None = None
    received_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=20_000)


class OfferRead(IdentifiedModel):
    """Offer representation returned by the API."""

    application_id: UUID
    base_salary: int | None
    bonus: int | None
    equity: str | None
    currency: str | None
    benefits: str | None
    decision: OfferDecision
    received_at: datetime | None
    notes: str | None
