"""Interview question service — CRUD for a user's question bank."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.models.interview_question import InterviewQuestion
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.schemas.interview_question import (
    InterviewQuestionCreate,
    InterviewQuestionUpdate,
)


class InterviewQuestionService:
    """Coordinates the interview question bank."""

    def __init__(self, session: Session) -> None:
        self.repo = InterviewQuestionRepository(session)
        self.applications = ApplicationRepository(session)

    def list_all(
        self,
        owner: User,
        *,
        tag: str | None = None,
        application_id: UUID | None = None,
    ) -> list[InterviewQuestion]:
        return self.repo.list_for_user(owner.id, tag=tag, application_id=application_id)

    def create(self, owner: User, data: InterviewQuestionCreate) -> InterviewQuestion:
        self._ensure_application_owned(owner, data.application_id)
        question = InterviewQuestion(user_id=owner.id, **_normalized(data.model_dump()))
        return self.repo.add(question)

    def get(self, owner: User, question_id: UUID) -> InterviewQuestion:
        return ensure_found(self.repo.get(owner.id, question_id), "Question not found.")

    def update(
        self, owner: User, question_id: UUID, data: InterviewQuestionUpdate
    ) -> InterviewQuestion:
        question = self.get(owner, question_id)
        changes = _normalized(data.model_dump(exclude_unset=True))
        # Read the id off the validated schema, not the widened dict, so the
        # ownership check keeps its type.
        if "application_id" in changes:
            self._ensure_application_owned(owner, data.application_id)
        for field, value in changes.items():
            setattr(question, field, value)
        self.repo.flush()
        return question

    def delete(self, owner: User, question_id: UUID) -> None:
        self.repo.delete(self.get(owner, question_id))

    def _ensure_application_owned(self, owner: User, application_id: UUID | None) -> None:
        """Validate that a referenced application exists and belongs to the user."""
        if application_id is None:
            return
        ensure_found(self.applications.get(owner.id, application_id), "Application not found.")


def _normalized(changes: dict[str, object]) -> dict[str, object]:
    """Tidy tags so filtering and display stay predictable.

    People type "System Design, Behavioural" with varied spacing and casing;
    storing a single canonical form keeps a tag filter from missing rows for
    cosmetic reasons.
    """
    if "tags" in changes:
        raw = changes["tags"]
        if isinstance(raw, str):
            tags = [part.strip().lower() for part in raw.split(",") if part.strip()]
            changes["tags"] = ", ".join(dict.fromkeys(tags)) or None
    return changes
