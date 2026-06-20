"""Note service — business logic for application notes."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.models.note import Note
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.note import NoteRepository
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    """Coordinates note persistence within an owned application."""

    def __init__(self, session: Session) -> None:
        self.repo = NoteRepository(session)
        self.applications = ApplicationRepository(session)

    def list_for_application(self, owner: User, application_id: UUID) -> list[Note]:
        self._ensure_application_owned(owner, application_id)
        return self.repo.list_for_application(owner.id, application_id)

    def create(self, owner: User, application_id: UUID, data: NoteCreate) -> Note:
        self._ensure_application_owned(owner, application_id)
        note = Note(user_id=owner.id, application_id=application_id, body=data.body)
        return self.repo.add(note)

    def get(self, owner: User, note_id: UUID) -> Note:
        return ensure_found(self.repo.get(owner.id, note_id), "Note not found.")

    def update(self, owner: User, note_id: UUID, data: NoteUpdate) -> Note:
        note = self.get(owner, note_id)
        note.body = data.body
        self.repo.flush()
        return note

    def delete(self, owner: User, note_id: UUID) -> None:
        note = self.get(owner, note_id)
        self.repo.delete(note)

    def _ensure_application_owned(self, owner: User, application_id: UUID) -> None:
        ensure_found(self.applications.get(owner.id, application_id), "Application not found.")
