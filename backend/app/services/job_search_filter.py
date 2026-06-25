"""JobSearchFilter service — CRUD for saved job-search criteria."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.models.job_search_filter import JobSearchFilter
from app.models.user import User
from app.repositories.job_search_filter import JobSearchFilterRepository
from app.schemas.job import JobSearchFilterCreate, JobSearchFilterUpdate


class JobSearchFilterService:
    """Coordinates job-search filter persistence."""

    def __init__(self, session: Session) -> None:
        self.repo = JobSearchFilterRepository(session)

    def list_all(self, owner: User) -> list[JobSearchFilter]:
        return self.repo.list_for_user(owner.id)

    def get(self, owner: User, filter_id: UUID) -> JobSearchFilter:
        return ensure_found(self.repo.get(owner.id, filter_id), "Filter not found.")

    def create(self, owner: User, data: JobSearchFilterCreate) -> JobSearchFilter:
        filt = JobSearchFilter(user_id=owner.id, **data.model_dump())
        return self.repo.add(filt)

    def update(self, owner: User, filter_id: UUID, data: JobSearchFilterUpdate) -> JobSearchFilter:
        filt = self.get(owner, filter_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(filt, field, value)
        self.repo.flush()
        return filt

    def delete(self, owner: User, filter_id: UUID) -> None:
        self.repo.delete(self.get(owner, filter_id))
