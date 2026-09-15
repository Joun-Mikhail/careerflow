"""Interview question endpoints: list, create, update, delete."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.interview_question import (
    InterviewQuestionCreate,
    InterviewQuestionRead,
    InterviewQuestionUpdate,
)
from app.services.interview_question import InterviewQuestionService

router = APIRouter(prefix="/interview-questions", tags=["interview-questions"])


@router.get(
    "",
    response_model=list[InterviewQuestionRead],
    summary="List the question bank, optionally by tag or application",
)
def list_questions(
    current_user: CurrentUser,
    db: DbSession,
    tag: str | None = Query(default=None, max_length=80),
    application_id: UUID | None = None,
) -> list[InterviewQuestionRead]:
    questions = InterviewQuestionService(db).list_all(
        current_user, tag=tag, application_id=application_id
    )
    return [InterviewQuestionRead.model_validate(item) for item in questions]


@router.post(
    "",
    response_model=InterviewQuestionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a question to the bank",
)
def create_question(
    data: InterviewQuestionCreate, current_user: CurrentUser, db: DbSession
) -> InterviewQuestionRead:
    return InterviewQuestionRead.model_validate(
        InterviewQuestionService(db).create(current_user, data)
    )


@router.patch(
    "/{question_id}",
    response_model=InterviewQuestionRead,
    summary="Update a question or its answer",
)
def update_question(
    question_id: UUID,
    data: InterviewQuestionUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> InterviewQuestionRead:
    return InterviewQuestionRead.model_validate(
        InterviewQuestionService(db).update(current_user, question_id, data)
    )


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a question",
)
def delete_question(question_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    InterviewQuestionService(db).delete(current_user, question_id)
