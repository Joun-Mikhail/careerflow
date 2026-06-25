"""JobSearchFilter repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc

from app.models.job_search_filter import JobSearchFilter
from app.repositories.base import BaseRepository


class JobSearchFilterRepository(BaseRepository[JobSearchFilter]):
    """Data access for :class:`JobSearchFilter`."""

    model = JobSearchFilter

    def list_for_user(self, owner_id: UUID) -> list[JobSearchFilter]:
        stmt = self.owned_query(owner_id).order_by(desc(JobSearchFilter.created_at))
        return list(self.session.execute(stmt).scalars())
