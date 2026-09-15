"""Contact repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, func, or_

from app.models.contact import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Data access for :class:`Contact`."""

    model = Contact

    def list_for_user(
        self,
        owner_id: UUID,
        *,
        search: str | None = None,
        company_id: UUID | None = None,
    ) -> list[Contact]:
        """Alphabetical by name, optionally filtered by company or free text."""
        stmt = self.owned_query(owner_id)
        if company_id is not None:
            stmt = stmt.where(Contact.company_id == company_id)
        if search and search.strip():
            needle = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Contact.name).like(needle),
                    func.lower(func.coalesce(Contact.role, "")).like(needle),
                    func.lower(func.coalesce(Contact.email, "")).like(needle),
                )
            )
        stmt = stmt.order_by(asc(func.lower(Contact.name)))
        return list(self.session.execute(stmt).scalars())
