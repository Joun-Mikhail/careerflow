"""CV repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, update

from app.models.cv import Cv
from app.repositories.base import BaseRepository


class CvRepository(BaseRepository[Cv]):
    """Data access for :class:`Cv`."""

    model = Cv

    def list_for_user(self, owner_id: UUID) -> list[Cv]:
        stmt = self.owned_query(owner_id).order_by(desc(Cv.is_default), desc(Cv.created_at))
        return list(self.session.execute(stmt).scalars())

    def clear_default(self, owner_id: UUID) -> None:
        """Unset the default flag on all of the user's CVs."""
        self.session.execute(
            update(Cv)
            .where(Cv.user_id == owner_id, Cv.is_default.is_(True))
            .values(is_default=False)
        )
        self.session.flush()
