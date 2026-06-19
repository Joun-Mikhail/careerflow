"""Application repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, desc

from app.core.pagination import PageParams
from app.models.application import Application
from app.models.enums import ApplicationStatus
from app.repositories.base import BaseRepository

SORTABLE_FIELDS = {
    "created_at": Application.created_at,
    "updated_at": Application.updated_at,
    "applied_at": Application.applied_at,
}


class ApplicationRepository(BaseRepository[Application]):
    """Data access for :class:`Application`."""

    model = Application
    soft_delete = True

    def list_applications(
        self,
        owner_id: UUID,
        *,
        params: PageParams,
        search: str | None = None,
        status: ApplicationStatus | None = None,
        company_id: UUID | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Application], int]:
        stmt = self.owned_query(owner_id)
        if search:
            stmt = stmt.where(self.ilike_contains(Application.role_title, search))
        if status is not None:
            stmt = stmt.where(Application.status == status)
        if company_id is not None:
            stmt = stmt.where(Application.company_id == company_id)

        column = SORTABLE_FIELDS.get(sort, Application.created_at)
        direction = asc if order == "asc" else desc
        # Sorting by a nullable column keeps NULLs last regardless of direction.
        stmt = stmt.order_by(direction(column), desc(Application.id))
        return self.paginate(stmt, params=params)
