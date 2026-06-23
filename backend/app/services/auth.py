"""Authentication service — registration, login, and token issuance.

Business rules live here, not in the router: email uniqueness, password
hashing, credential verification, and access-token creation. The service is
deliberately framework-agnostic and depends only on the repository, the
security primitives, and configuration.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AuthenticationError, ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import AuthResponse, Token, UserCreate, UserRead

settings = get_settings()


class AuthService:
    """Coordinates account creation and credential verification."""

    def __init__(self, session: Session) -> None:
        self.users = UserRepository(session)

    def register(self, data: UserCreate) -> AuthResponse:
        """Create a new account, rejecting duplicate emails."""
        normalized_email = data.email.strip().lower()
        if self.users.email_exists(normalized_email):
            raise ConflictError("An account with this email already exists.")

        user = User(
            email=normalized_email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        self.users.add(user)
        return self._auth_response(user)

    def authenticate(self, email: str, password: str) -> AuthResponse:
        """Verify credentials and issue a token, or raise on failure.

        Returns a generic error on any failure (unknown email, wrong password,
        or inactive account) to avoid user enumeration.
        """
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("Invalid email or password.")
        return self._auth_response(user)

    def update_profile(self, user: User, full_name: str | None) -> User:
        """Update the user's editable profile fields."""
        user.full_name = full_name
        self.users.flush()
        return user

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """Change the password after verifying the current one."""
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect.")
        user.hashed_password = hash_password(new_password)
        self.users.flush()

    def _auth_response(self, user: User) -> AuthResponse:
        token = create_access_token(user.id)
        return AuthResponse(
            user=UserRead.model_validate(user),
            token=Token(
                access_token=token,
                expires_in=settings.access_token_expire_minutes * 60,
            ),
        )
