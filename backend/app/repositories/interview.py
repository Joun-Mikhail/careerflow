"""Interview repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, desc

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
