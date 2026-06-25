"""Job-search filter endpoints: CRUD + run a search."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.job import (
    JobRead,
    JobSearchFilterCreate,
    JobSearchFilterRead,
    JobSearchFilterUpdate,
)
from app.services.job import JobService
from app.services.job_search_filter import JobSearchFilterService

router = APIRouter(prefix="/job-filters", tags=["job-search"])


@router.get("", response_model=list[JobSearchFilterRead], summary="List saved filters")
def list_filters(current_user: CurrentUser, db: DbSession) -> list[JobSearchFilterRead]:
    items = JobSearchFilterService(db).list_all(current_user)
    return [JobSearchFilterRead.model_validate(item) for item in items]


@router.post(
    "",
    response_model=JobSearchFilterRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job-search filter",
)
def create_filter(
    data: JobSearchFilterCreate, current_user: CurrentUser, db: DbSession
) -> JobSearchFilterRead:
    return JobSearchFilterRead.model_validate(JobSearchFilterService(db).create(current_user, data))


@router.patch("/{filter_id}", response_model=JobSearchFilterRead, summary="Update a filter")
def update_filter(
    filter_id: UUID, data: JobSearchFilterUpdate, current_user: CurrentUser, db: DbSession
) -> JobSearchFilterRead:
    filt = JobSearchFilterService(db).update(current_user, filter_id, data)
    return JobSearchFilterRead.model_validate(filt)


@router.delete("/{filter_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a filter")
def delete_filter(filter_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    JobSearchFilterService(db).delete(current_user, filter_id)


@router.post(
    "/{filter_id}/search",
    response_model=list[JobRead],
    summary="Run a saved filter against the job source and store the results",
)
def run_search(filter_id: UUID, current_user: CurrentUser, db: DbSession) -> list[JobRead]:
    jobs = JobService(db).run_search(current_user, filter_id)
    return [JobRead.model_validate(job) for job in jobs]
