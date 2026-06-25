"""Job service — run a filter against a provider and store normalized jobs."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.core.logging import log_action
from app.models.job import Job
from app.models.user import User
from app.repositories.job import JobRepository
from app.repositories.job_search_filter import JobSearchFilterRepository
from app.services.job_provider import JobPosting, JobProvider, get_job_provider


class JobService:
    """Fetches jobs from the configured provider and persists them."""

    def __init__(self, session: Session, provider: JobProvider | None = None) -> None:
        self.repo = JobRepository(session)
        self.filters = JobSearchFilterRepository(session)
        self.provider = provider or get_job_provider()

    def list_all(self, owner: User, *, limit: int = 100) -> list[Job]:
        return self.repo.list_for_user(owner.id, limit=limit)

    def get(self, owner: User, job_id: UUID) -> Job:
        return ensure_found(self.repo.get(owner.id, job_id), "Job not found.")

    def run_search(self, owner: User, filter_id: UUID, *, limit: int = 20) -> list[Job]:
        """Run a saved filter, upsert results, and return the matching jobs."""
        filt = ensure_found(self.filters.get(owner.id, filter_id), "Filter not found.")
        postings = self.provider.search(filt, limit=limit)
        jobs = [self._upsert(owner.id, posting) for posting in postings]
        log_action(
            "jobs_fetched",
            status="ok",
            user_id=owner.id,
            provider=self.provider.name,
            count=len(jobs),
        )
        return jobs

    def _upsert(self, owner_id: UUID, posting: JobPosting) -> Job:
        existing = self.repo.get_by_external(owner_id, self.provider.name, posting.external_id)
        if existing is not None:
            # Refresh the mutable fields in case the posting changed.
            existing.title = posting.title
            existing.company = posting.company
            existing.location = posting.location
            existing.description = posting.description
            existing.url = posting.url
            existing.salary_min = posting.salary_min
            existing.salary_max = posting.salary_max
            existing.remote = posting.remote
            existing.posted_at = posting.posted_at
            self.repo.flush()
            return existing
        job = Job(
            user_id=owner_id,
            source=self.provider.name,
            external_id=posting.external_id,
            title=posting.title,
            company=posting.company,
            location=posting.location,
            description=posting.description,
            url=posting.url,
            salary_min=posting.salary_min,
            salary_max=posting.salary_max,
            remote=posting.remote,
            posted_at=posting.posted_at,
        )
        return self.repo.add(job)
