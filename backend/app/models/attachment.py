"""Attachment model — metadata for an uploaded document.

The file bytes live on disk under the configured upload directory; this row
holds only metadata and an opaque ``stored_filename`` used to locate the file.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AttachmentKind

if TYPE_CHECKING:
    from app.models.application import Application


class Attachment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Metadata describing a document uploaded for an application."""

    __tablename__ = "attachments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    kind: Mapped[AttachmentKind] = mapped_column(
        SAEnum(
            AttachmentKind,
            name="attachment_kind",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    application: Mapped[Application] = relationship(back_populates="attachments")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Attachment id={self.id} kind={self.kind} name={self.original_filename!r}>"
