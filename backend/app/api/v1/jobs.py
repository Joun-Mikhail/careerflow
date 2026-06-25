"""Job endpoints: list fetched jobs."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.job import JobRead
from app.services.job import JobService

router = APIRouter(prefix="/jobs", tags=["job-search"])


@router.get("", response_model=list[JobRead], summary="List jobs fetched for the current user")
def list_jobs(current_user: CurrentUser, db: DbSession) -> list[JobRead]:
    return [JobRead.model_validate(job) for job in JobService(db).list_all(current_user)]
