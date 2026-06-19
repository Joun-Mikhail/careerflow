"""Note repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc

from app.models.note import Note
from app.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """Data access for :class:`Note`."""

    model = Note

    def list_for_application(self, owner_id: UUID, application_id: UUID) -> list[Note]:
        """Return notes for an application, newest first."""
        stmt = (
            self.owned_query(owner_id)
            .where(Note.application_id == application_id)
            .order_by(desc(Note.created_at))
        )
        return list(self.session.execute(stmt).scalars())
