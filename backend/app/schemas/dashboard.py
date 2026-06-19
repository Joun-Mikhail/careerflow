"""Schemas for the dashboard summary."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import InterviewMode, InterviewResult
from app.schemas.application import ApplicationRead


class DashboardTotals(BaseModel):
    """Headline counts shown at the top of the dashboard."""

    applications: int
    interviews: int
    offers: int
    rejections: int
    accepted: int
    pending_tasks: int


class UpcomingInterview(BaseModel):
    """A compact interview view for the dashboard's upcoming list."""

    id: UUID
    application_id: UUID
    role_title: str | None
    scheduled_at: datetime
    mode: InterviewMode
    result: InterviewResult


class PendingTaskSummary(BaseModel):
    """A compact task view for the dashboard's pending list."""

    id: UUID
    title: str
    priority: str
    due_at: datetime | None


class DashboardSummary(BaseModel):
    """Everything the dashboard needs in a single response."""

    totals: DashboardTotals
    success_rate: float
    upcoming_interviews: list[UpcomingInterview]
    pending_tasks: list[PendingTaskSummary]
    recent_applications: list[ApplicationRead]
