"""Interview repository — user-scoped persistence and querying."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import asc, desc

from app.core.pagination import PageParams
from app.models.interview import Interview
from app.repositories.base import BaseRepository


class InterviewRepository(BaseRepository[Interview]):
    """Data access for :class:`Interview`."""

    model = Interview

    def list_for_application(
        self, owner_id: UUID, application_id: UUID, *, order: str = "asc"
    ) -> list[Interview]:
        """Return all interviews for an application, ordered by schedule."""
        direction = asc if order == "asc" else desc
        stmt = (
            self.owned_query(owner_id)
            .where(Interview.application_id == application_id)
            .order_by(direction(Interview.scheduled_at))
        )
        return list(self.session.execute(stmt).scalars())

    def list_interviews(
        self,
        owner_id: UUID,
        *,
        params: PageParams,
        scope: str = "all",
        now: datetime,
    ) -> tuple[list[Interview], int]:
        """Return all of a user's interviews, optionally split into upcoming/past.

        ``scope`` is one of ``"all"``, ``"upcoming"`` (>= now, soonest first), or
        ``"past"`` (< now, most recent first).
        """
        stmt = self.owned_query(owner_id)
        if scope == "upcoming":
            stmt = stmt.where(Interview.scheduled_at >= now).order_by(asc(Interview.scheduled_at))
        elif scope == "past":
            stmt = stmt.where(Interview.scheduled_at < now).order_by(desc(Interview.scheduled_at))
        else:
            stmt = stmt.order_by(desc(Interview.scheduled_at))
        return self.paginate(stmt, params=params)
