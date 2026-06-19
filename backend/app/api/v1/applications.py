"""Application endpoints: CRUD with search, filtering, sorting, pagination."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, Pagination
from app.core.pagination import Page
from app.models.enums import ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.services.application import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=Page[ApplicationRead], summary="List applications")
def list_applications(
    current_user: CurrentUser,
    db: DbSession,
    pagination: Pagination,
    q: Annotated[str | None, Query(description="Search by role title.")] = None,
    status_filter: Annotated[
        ApplicationStatus | None, Query(alias="status", description="Filter by status.")
    ] = None,
    company_id: Annotated[UUID | None, Query(description="Filter by company.")] = None,
    sort: Literal["created_at", "updated_at", "applied_at"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[ApplicationRead]:
    return ApplicationService(db).list(
        current_user,
        params=pagination,
        search=q,
        status=status_filter,
        company_id=company_id,
        sort=sort,
        order=order,
    )


@router.post(
    "",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an application",
)
def create_application(
    data: ApplicationCreate, current_user: CurrentUser, db: DbSession
) -> ApplicationRead:
    application = ApplicationService(db).create(current_user, data)
    return ApplicationRead.model_validate(application)


@router.get("/{application_id}", response_model=ApplicationRead, summary="Get an application")
def get_application(
    application_id: UUID, current_user: CurrentUser, db: DbSession
) -> ApplicationRead:
    application = ApplicationService(db).get(current_user, application_id)
    return ApplicationRead.model_validate(application)


@router.patch("/{application_id}", response_model=ApplicationRead, summary="Update an application")
def update_application(
    application_id: UUID,
    data: ApplicationUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> ApplicationRead:
    application = ApplicationService(db).update(current_user, application_id, data)
    return ApplicationRead.model_validate(application)


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an application (soft delete)",
)
def delete_application(application_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    ApplicationService(db).delete(current_user, application_id)
