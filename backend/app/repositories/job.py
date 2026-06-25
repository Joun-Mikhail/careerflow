"""Job repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc

from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Data access for :class:`Job`."""

    model = Job

    def list_for_user(self, owner_id: UUID, *, limit: int = 100) -> list[Job]:
        stmt = self.owned_query(owner_id).order_by(desc(Job.created_at)).limit(limit)
        return list(self.session.execute(stmt).scalars())

    def get_by_external(self, owner_id: UUID, source: str, external_id: str) -> Job | None:
        stmt = self.owned_query(owner_id).where(
            Job.source == source, Job.external_id == external_id
        )
        return self.session.execute(stmt).scalar_one_or_none()
