"""Schemas for interview resources."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import InterviewMode, InterviewResult
from app.schemas.base import IdentifiedModel


class InterviewBase(BaseModel):
    """Fields shared by create and update payloads."""

    scheduled_at: datetime
    round_type: str | None = Field(default=None, max_length=80)
    interviewer: str | None = Field(default=None, max_length=200)
    mode: InterviewMode = InterviewMode.VIDEO
    result: InterviewResult = InterviewResult.PENDING
    notes: str | None = Field(default=None, max_length=20_000)


class InterviewCreate(InterviewBase):
    """Payload for creating an interview."""


class InterviewUpdate(BaseModel):
    """Payload for partially updating an interview (all fields optional)."""

    scheduled_at: datetime | None = None
    round_type: str | None = Field(default=None, max_length=80)
    interviewer: str | None = Field(default=None, max_length=200)
    mode: InterviewMode | None = None
    result: InterviewResult | None = None
    notes: str | None = Field(default=None, max_length=20_000)


class InterviewRead(IdentifiedModel):
    """Interview representation returned by the API."""

    application_id: UUID
    scheduled_at: datetime
    round_type: str | None
    interviewer: str | None
    mode: InterviewMode
    result: InterviewResult
    notes: str | None
