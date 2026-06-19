"""Shared model building blocks: portable UUID type and common mixins.

These utilities let the same ORM models run against PostgreSQL in production
and SQLite in tests without conditional logic in each model.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, TypeDecorator
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column


def utcnow() -> datetime:
    """Return a timezone-aware current UTC timestamp."""
    return datetime.now(UTC)


class GUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL's native ``UUID`` when available and falls back to a
    ``CHAR(32)`` hex string elsewhere (e.g. SQLite), so primary keys behave
    identically across environments.
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[no-untyped-def]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        return dialect.type_descriptor(String(32))

    def process_bind_param(self, value, dialect):  # type: ignore[no-untyped-def]
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        if dialect.name == "postgresql":
            return value
        return value.hex

    def process_result_value(self, value, dialect):  # type: ignore[no-untyped-def]
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class UUIDPrimaryKeyMixin:
    """Adds a UUID primary key generated on the Python side."""

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, sort_order=-100
    )


class TimestampMixin:
    """Adds ``created_at`` / ``updated_at`` columns maintained by the ORM."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, sort_order=100
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
        sort_order=101,
    )


class SoftDeleteMixin:
    """Adds a nullable ``deleted_at`` column for soft deletion."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True, sort_order=102
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
