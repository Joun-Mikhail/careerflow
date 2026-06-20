"""Company repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from app.core.pagination import PageParams
from app.models.company import Company
from app.repositories.base import BaseRepository

# Fields a client may sort companies by, mapped to model columns.
SORTABLE_FIELDS = {
    "created_at": Company.created_at,
    "updated_at": Company.updated_at,
    "name": Company.name,
}


class CompanyRepository(BaseRepository[Company]):
    """Data access for :class:`Company`."""

    model = Company
    soft_delete = True

    def list_companies(
        self,
        owner_id: UUID,
        *,
        params: PageParams,
        search: str | None = None,
        industry: str | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Company], int]:
        stmt = self.owned_query(owner_id)
        if search:
            stmt = stmt.where(self.ilike_contains(Company.name, search))
        if industry:
            stmt = stmt.where(Company.industry == industry)

        stmt = self.apply_sort(
            stmt, sortable=SORTABLE_FIELDS, sort=sort, order=order, default=Company.created_at
        )
        return self.paginate(stmt, params=params)
