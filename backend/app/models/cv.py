"""CV model — a stored or AI-tailored curriculum vitae in the document vault.

A CV is either an uploaded file (PDF/DOCX, bytes held by the storage backend)
or an AI-tailored text version derived from another CV for a specific job.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import CvSource

if TYPE_CHECKING:
    from app.models.user import User


class Cv(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A CV owned by a user, either uploaded or AI-tailored."""

    __tablename__ = "cvs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[CvSource] = mapped_column(
        SAEnum(
            CvSource,
            name="cv_source",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=CvSource.UPLOADED,
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # File-backed CVs (source == uploaded): bytes live in the storage backend.
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stored_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Text-backed CVs (source == ai_tailored, or parsed text of an upload).
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Provenance for tailored CVs: the CV it was derived from and the job it
    # was tailored for. Both keep the row if the parent/job disappears.
    parent_cv_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cvs.id", ondelete="SET NULL"), nullable=True
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped[User] = relationship(back_populates="cvs")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Cv id={self.id} title={self.title!r} source={self.source}>"
