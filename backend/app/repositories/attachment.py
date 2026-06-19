"""Attachment repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc

from app.models.attachment import Attachment
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[Attachment]):
    """Data access for :class:`Attachment` metadata."""

    model = Attachment

    def list_for_application(self, owner_id: UUID, application_id: UUID) -> list[Attachment]:
        stmt = (
            self.owned_query(owner_id)
            .where(Attachment.application_id == application_id)
            .order_by(desc(Attachment.created_at))
        )
        return list(self.session.execute(stmt).scalars())
