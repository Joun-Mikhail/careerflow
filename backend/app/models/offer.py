"""Offer model — a compensation offer received for an application."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import OfferDecision

if TYPE_CHECKING:
    from app.models.application import Application


class Offer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A compensation offer tied to an application."""

    __tablename__ = "offers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    base_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bonus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    equity: Mapped[str | None] = mapped_column(String(200), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[OfferDecision] = mapped_column(
        SAEnum(
            OfferDecision,
            name="offer_decision",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=OfferDecision.PENDING,
        nullable=False,
    )
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    application: Mapped[Application] = relationship(back_populates="offers")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Offer id={self.id} application_id={self.application_id} decision={self.decision}>"
