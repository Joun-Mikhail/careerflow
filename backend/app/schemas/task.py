"""Schemas for task resources."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import TaskPriority
from app.schemas.base import IdentifiedModel


class TaskBase(BaseModel):
    """Fields shared by create and update payloads."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=20_000)
    priority: TaskPriority = TaskPriority.MEDIUM
    due_at: datetime | None = None
    application_id: UUID | None = None


class TaskCreate(TaskBase):
    """Payload for creating a task."""


class TaskUpdate(BaseModel):
    """Payload for partially updating a task (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=20_000)
    priority: TaskPriority | None = None
    due_at: datetime | None = None
    application_id: UUID | None = None
    is_completed: bool | None = None


class TaskRead(IdentifiedModel):
    """Task representation returned by the API."""

    title: str
    description: str | None
    priority: TaskPriority
    due_at: datetime | None
    application_id: UUID | None
    is_completed: bool
    completed_at: datetime | None
