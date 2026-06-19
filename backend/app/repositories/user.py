"""User repository — persistence for accounts."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for :class:`User`. Users are not user-scoped themselves."""

    model = User

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Look up a user by email, case-insensitively."""
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.session.execute(stmt).scalar_one_or_none()

    def email_exists(self, email: str) -> bool:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(func.lower(User.email) == email.strip().lower())
        )
        return bool(self.session.execute(stmt).scalar_one())
