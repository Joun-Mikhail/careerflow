"""Generic repository base class.

Concrete repositories inherit from :class:`BaseRepository`, which centralizes
the patterns every aggregate shares: user-scoped queries, soft-delete
awareness, fetch-by-id, persistence, and offset pagination. Keeping these here
avoids duplicating query plumbing across every entity.
"""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import ColumnElement, Select, func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.core.database import Base
from app.core.pagination import PageParams
from app.models.base import utcnow

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Common data-access behaviour scoped to a single owning user."""

    model: type[ModelT]
    #: Whether the model carries a ``deleted_at`` column for soft deletion.
    soft_delete: bool = False

    def __init__(self, session: Session) -> None:
        self.session = session

    # -- Query construction --------------------------------------------------
    def owned_query(self, owner_id: UUID) -> Select[tuple[ModelT]]:
        """Return a base SELECT scoped to ``owner_id`` (and not soft-deleted)."""
        stmt = select(self.model).where(self.model.user_id == owner_id)  # type: ignore[attr-defined]
        if self.soft_delete:
            stmt = stmt.where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]
        return stmt

    # -- Reads ---------------------------------------------------------------
    def get(self, owner_id: UUID, entity_id: UUID) -> ModelT | None:
        """Fetch one entity by id, scoped to its owner; ``None`` if missing."""
        stmt = self.owned_query(owner_id).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        return self.session.execute(stmt).scalar_one_or_none()

    def paginate(
        self,
        stmt: Select[tuple[ModelT]],
        *,
        params: PageParams,
    ) -> tuple[list[ModelT], int]:
        """Run ``stmt`` with offset pagination, returning ``(items, total)``."""
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = self.session.execute(count_stmt).scalar_one()
        rows = self.session.execute(stmt.offset(params.offset).limit(params.limit)).scalars()
        return list(rows), int(total)

    # -- Writes --------------------------------------------------------------
    def add(self, entity: ModelT) -> ModelT:
        """Persist a new entity and flush so its identity is populated."""
        self.session.add(entity)
        self.session.flush()
        return entity

    def flush(self) -> None:
        self.session.flush()

    def delete(self, entity: ModelT) -> None:
        """Soft-delete when supported, otherwise hard-delete."""
        if self.soft_delete:
            entity.deleted_at = utcnow()  # type: ignore[attr-defined]
            self.session.flush()
        else:
            self.session.delete(entity)
            self.session.flush()

    # -- Helpers -------------------------------------------------------------
    @staticmethod
    def ilike_contains(column: InstrumentedAttribute[str], term: str) -> ColumnElement[bool]:
        """Case-insensitive ``contains`` predicate for search inputs."""
        return column.ilike(f"%{term}%")
