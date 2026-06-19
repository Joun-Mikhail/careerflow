"""Interview service — business logic for interview rounds."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.interview import Interview
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.interview import InterviewRepository
from app.schemas.interview import InterviewCreate, InterviewUpdate


class InterviewService:
    """Coordinates interview persistence within an owned application."""

    def __init__(self, session: Session) -> None:
        self.repo = InterviewRepository(session)
        self.applications = ApplicationRepository(session)

    def list_for_application(self, owner: User, application_id: UUID) -> list[Interview]:
        self._ensure_application_owned(owner, application_id)
        return self.repo.list_for_application(owner.id, application_id)

    def create(self, owner: User, application_id: UUID, data: InterviewCreate) -> Interview:
        self._ensure_application_owned(owner, application_id)
        interview = Interview(user_id=owner.id, application_id=application_id, **data.model_dump())
        return self.repo.add(interview)

    def get(self, owner: User, interview_id: UUID) -> Interview:
        interview = self.repo.get(owner.id, interview_id)
        if interview is None:
            raise NotFoundError("Interview not found.")
        return interview

    def update(self, owner: User, interview_id: UUID, data: InterviewUpdate) -> Interview:
        interview = self.get(owner, interview_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(interview, field, value)
        self.repo.flush()
        return interview

    def delete(self, owner: User, interview_id: UUID) -> None:
        interview = self.get(owner, interview_id)
        self.repo.delete(interview)

    def _ensure_application_owned(self, owner: User, application_id: UUID) -> None:
        if self.applications.get(owner.id, application_id) is None:
            raise NotFoundError("Application not found.")
