"""JobSearchFilter model — saved criteria for fetching external jobs."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.automation_rule import AutomationRule
    from app.models.user import User


class JobSearchFilter(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A reusable set of criteria used to query external job sources."""

    __tablename__ = "job_search_filters"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    # Comma-separated free-text fields kept simple/portable; parsed in the service layer.
    title_keywords: Mapped[str | None] = mapped_column(String(500), nullable=True)
    locations: Mapped[str | None] = mapped_column(String(500), nullable=True)
    keywords: Mapped[str | None] = mapped_column(String(500), nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship(back_populates="job_search_filters")
    automation_rules: Mapped[list[AutomationRule]] = relationship(
        back_populates="filter", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<JobSearchFilter id={self.id} name={self.name!r}>"
