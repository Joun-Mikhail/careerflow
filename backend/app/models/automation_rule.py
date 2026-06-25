"""AutomationRule model — scheduled job-search automation for a filter."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RunFrequency

if TYPE_CHECKING:
    from app.models.job_search_filter import JobSearchFilter
    from app.models.user import User


class AutomationRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Defines how a saved filter is run automatically by a scheduler.

    The scheduler itself is external; the backend only exposes an entrypoint
    that processes due rules. Defaults are conservative (disabled, no
    auto-apply) so automation is strictly opt-in.
    """

    __tablename__ = "automation_rules"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    filter_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("job_search_filters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    run_frequency: Mapped[RunFrequency] = mapped_column(
        SAEnum(
            RunFrequency,
            name="run_frequency",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=RunFrequency.MANUAL,
        nullable=False,
    )
    max_applications_per_run: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    auto_tailor_cv: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_create_application: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="automation_rules")
    filter: Mapped[JobSearchFilter] = relationship(back_populates="automation_rules")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<AutomationRule id={self.id} enabled={self.is_enabled} freq={self.run_frequency}>"
