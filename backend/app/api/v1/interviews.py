"""Interview endpoints, nested under applications and addressable directly."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, Pagination
from app.core.pagination import Page
from app.schemas.interview import InterviewCreate, InterviewRead, InterviewUpdate
from app.services.interview import InterviewService

# Two routers share the interview service: one nested under an application for
# listing/creating, one at the top level for addressing a specific interview.
router = APIRouter(tags=["interviews"])


@router.get("/interviews", response_model=Page[InterviewRead], summary="List all interviews")
def list_all_interviews(
    current_user: CurrentUser,
    db: DbSession,
    pagination: Pagination,
    scope: Annotated[
        Literal["all", "upcoming", "past"],
        Query(description="Filter by schedule relative to now."),
    ] = "all",
) -> Page[InterviewRead]:
    return InterviewService(db).list_all(current_user, params=pagination, scope=scope)


@router.get(
    "/applications/{application_id}/interviews",
    response_model=list[InterviewRead],
    summary="List interviews for an application",
)
def list_interviews(
    application_id: UUID, current_user: CurrentUser, db: DbSession
) -> list[InterviewRead]:
    interviews = InterviewService(db).list_for_application(current_user, application_id)
    return [InterviewRead.model_validate(item) for item in interviews]


@router.post(
    "/applications/{application_id}/interviews",
    response_model=InterviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an interview for an application",
)
def create_interview(
    application_id: UUID,
    data: InterviewCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> InterviewRead:
    interview = InterviewService(db).create(current_user, application_id, data)
    return InterviewRead.model_validate(interview)


@router.get("/interviews/{interview_id}", response_model=InterviewRead, summary="Get an interview")
def get_interview(interview_id: UUID, current_user: CurrentUser, db: DbSession) -> InterviewRead:
    return InterviewRead.model_validate(InterviewService(db).get(current_user, interview_id))


@router.patch(
    "/interviews/{interview_id}", response_model=InterviewRead, summary="Update an interview"
)
def update_interview(
    interview_id: UUID,
    data: InterviewUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> InterviewRead:
    interview = InterviewService(db).update(current_user, interview_id, data)
    return InterviewRead.model_validate(interview)


@router.delete(
    "/interviews/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an interview",
)
def delete_interview(interview_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    InterviewService(db).delete(current_user, interview_id)
