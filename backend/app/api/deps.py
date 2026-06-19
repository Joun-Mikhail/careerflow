"""Shared FastAPI dependencies.

These wire HTTP concerns (the request, the DB session, the bearer token) to the
service layer. Authentication resolves the current :class:`User` from a JWT and
is the gate every protected endpoint depends on.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AuthenticationError
from app.core.pagination import MAX_PAGE_SIZE, PageParams
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository

# ``auto_error=False`` lets us raise our own AuthenticationError (mapped to a
# consistent 401 envelope) instead of FastAPI's default response shape.
_bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> User:
    """Resolve and return the authenticated, active user.

    Raises :class:`AuthenticationError` (HTTP 401) when the token is missing,
    invalid, or refers to a missing/inactive account.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Not authenticated.")

    user_id = decode_access_token(credentials.credentials)
    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("Could not validate credentials.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_page_params(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
) -> PageParams:
    """Parse common pagination query parameters into a :class:`PageParams`."""
    return PageParams(page=page, page_size=page_size)


Pagination = Annotated[PageParams, Depends(get_page_params)]
