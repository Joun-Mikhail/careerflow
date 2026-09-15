"""Schemas for the interview question bank."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestionBase(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    answer: str | None = Field(default=None, max_length=10_000)
    # Free-text labels, comma-separated: "system design, behavioural".
    tags: str | None = Field(default=None, max_length=300)
    application_id: UUID | None = None
    asked: bool = False


class InterviewQuestionCreate(InterviewQuestionBase):
    pass


class InterviewQuestionUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=2_000)
    answer: str | None = Field(default=None, max_length=10_000)
    tags: str | None = Field(default=None, max_length=300)
    application_id: UUID | None = None
    asked: bool | None = None


class InterviewQuestionRead(InterviewQuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
