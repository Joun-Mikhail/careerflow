"""Aggregation queries powering the dashboard and analytics endpoints.

All queries are user-scoped and written to run identically on PostgreSQL and
SQLite. Time-bucketing (e.g. applications per month) is performed in Python
rather than with database-specific date functions to keep the queries portable;
the data volumes for a personal job search make this comfortably cheap.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.company import Company
from app.models.enums import ApplicationStatus
from app.models.interview import Interview
from app.models.task import Task


class StatsRepository:
    """Read-only aggregate queries for a single user's data."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # -- Applications --------------------------------------------------------
    def _active_applications(self, owner_id: UUID):  # type: ignore[no-untyped-def]
        return (
            select(Application)
            .where(Application.user_id == owner_id)
            .where(Application.deleted_at.is_(None))
        )

    def count_applications(self, owner_id: UUID) -> int:
        stmt = select(func.count()).select_from(self._active_applications(owner_id).subquery())
        return int(self.session.execute(stmt).scalar_one())

    def status_distribution(self, owner_id: UUID) -> dict[ApplicationStatus, int]:
        stmt = (
            select(Application.status, func.count())
            .where(Application.user_id == owner_id)
            .where(Application.deleted_at.is_(None))
            .group_by(Application.status)
        )
        counts = dict.fromkeys(ApplicationStatus, 0)
        for status, count in self.session.execute(stmt):
            counts[status] = int(count)
        return counts

    def industry_distribution(self, owner_id: UUID) -> dict[str, int]:
        stmt = (
            select(func.coalesce(Company.industry, "Unknown"), func.count())
            .select_from(Application)
            .join(Company, Application.company_id == Company.id)
            .where(Application.user_id == owner_id)
            .where(Application.deleted_at.is_(None))
            .group_by(Company.industry)
        )
        return {str(industry): int(count) for industry, count in self.session.execute(stmt)}

    def application_dates(self, owner_id: UUID, *, since: datetime) -> list[datetime]:
        """Return the reference date (applied_at or created_at) per application."""
        stmt = (
            select(func.coalesce(Application.applied_at, Application.created_at))
            .where(Application.user_id == owner_id)
            .where(Application.deleted_at.is_(None))
        )
        dates = [row[0] for row in self.session.execute(stmt)]
        return [d for d in dates if d is not None and d >= since]

    # -- Interviews ----------------------------------------------------------
    def count_interviews(self, owner_id: UUID) -> int:
        stmt = select(func.count()).select_from(
            select(Interview).where(Interview.user_id == owner_id).subquery()
        )
        return int(self.session.execute(stmt).scalar_one())

    def count_applications_with_interviews(self, owner_id: UUID) -> int:
        stmt = select(func.count(func.distinct(Interview.application_id))).where(
            Interview.user_id == owner_id
        )
        return int(self.session.execute(stmt).scalar_one())

    def upcoming_interviews(
        self, owner_id: UUID, *, now: datetime, limit: int = 5
    ) -> list[Interview]:
        stmt = (
            select(Interview)
            .where(Interview.user_id == owner_id)
            .where(Interview.scheduled_at >= now)
            .order_by(Interview.scheduled_at.asc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars())

    # -- Tasks ---------------------------------------------------------------
    def count_pending_tasks(self, owner_id: UUID) -> int:
        stmt = select(func.count()).where(Task.user_id == owner_id, Task.is_completed.is_(False))
        return int(self.session.execute(stmt).scalar_one())

    def pending_tasks(self, owner_id: UUID, *, limit: int = 5) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.user_id == owner_id, Task.is_completed.is_(False))
            .order_by(Task.due_at.is_(None), Task.due_at.asc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars())

    def recent_applications(self, owner_id: UUID, *, limit: int = 5) -> list[Application]:
        stmt = (
            self._active_applications(owner_id).order_by(Application.created_at.desc()).limit(limit)
        )
        return list(self.session.execute(stmt).scalars())
