"""Certificate repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc

from app.models.certificate import Certificate
from app.repositories.base import BaseRepository


class CertificateRepository(BaseRepository[Certificate]):
    """Data access for :class:`Certificate`."""

    model = Certificate

    def list_for_user(self, owner_id: UUID) -> list[Certificate]:
        stmt = self.owned_query(owner_id).order_by(
            desc(Certificate.issued_on), desc(Certificate.created_at)
        )
        return list(self.session.execute(stmt).scalars())
