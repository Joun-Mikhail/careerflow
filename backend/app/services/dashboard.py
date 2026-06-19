"""Dashboard service — assembles the summary view from aggregate stats."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.models.enums import ApplicationStatus
from app.models.user import User
from app.repositories.stats import StatsRepository
from app.schemas.application import ApplicationRead
from app.schemas.dashboard import (
    DashboardSummary,
    DashboardTotals,
    PendingTaskSummary,
    UpcomingInterview,
)


class DashboardService:
    """Builds the dashboard summary for a user."""

    def __init__(self, session: Session) -> None:
        self.stats = StatsRepository(session)

    def summary(self, owner: User) -> DashboardSummary:
        distribution = self.stats.status_distribution(owner.id)
        total_applications = sum(distribution.values())
        offers = distribution[ApplicationStatus.OFFER]
        accepted = distribution[ApplicationStatus.ACCEPTED]
        rejections = distribution[ApplicationStatus.REJECTED]

        totals = DashboardTotals(
            applications=total_applications,
            interviews=self.stats.count_interviews(owner.id),
            offers=offers,
            rejections=rejections,
            accepted=accepted,
            pending_tasks=self.stats.count_pending_tasks(owner.id),
        )

        # Success rate: share of applications that reached an offer or better.
        successes = offers + accepted
        success_rate = round(successes / total_applications * 100, 1) if total_applications else 0.0

        upcoming = [
            UpcomingInterview(
                id=interview.id,
                application_id=interview.application_id,
                role_title=interview.application.role_title if interview.application else None,
                scheduled_at=interview.scheduled_at,
                mode=interview.mode,
                result=interview.result,
            )
            for interview in self.stats.upcoming_interviews(owner.id, now=utcnow())
        ]

        pending_tasks = [
            PendingTaskSummary(
                id=task.id, title=task.title, priority=task.priority, due_at=task.due_at
            )
            for task in self.stats.pending_tasks(owner.id)
        ]

        recent = [
            ApplicationRead.model_validate(application)
            for application in self.stats.recent_applications(owner.id)
        ]

        return DashboardSummary(
            totals=totals,
            success_rate=success_rate,
            upcoming_interviews=upcoming,
            pending_tasks=pending_tasks,
            recent_applications=recent,
        )
