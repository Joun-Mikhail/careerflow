"""Contact model — a recruiter, hiring manager or referrer."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class Contact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A person in the user's job search, optionally tied to a company.

    Everything but the name is optional: contacts are usually captured mid
    conversation from whatever the user happens to know, and a form that
    demands an email address before it will save a name is a form people
    route around.
    """

    __tablename__ = "contacts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # The person outlives the company record; deleting a company should not
    # silently take its recruiters with it.
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("companies.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="contacts")
    company: Mapped[Company | None] = relationship(back_populates="contacts")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Contact id={self.id} name={self.name!r}>"
