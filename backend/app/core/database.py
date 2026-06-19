"""Database engine, session factory, and declarative base.

The application uses synchronous SQLAlchemy 2.0. A synchronous stack keeps the
service and repository layers simple to reason about and trivial to test
against an in-memory SQLite database, while FastAPI still serves requests
concurrently by running synchronous path operations in a worker threadpool.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def _engine_kwargs(url: str) -> dict[str, object]:
    """Build engine keyword arguments appropriate to the backend.

    SQLite (used in tests) needs ``check_same_thread=False`` so a connection
    can be shared across the TestClient's threadpool; PostgreSQL benefits from
    pre-ping to recover gracefully from dropped connections.
    """
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
    **_engine_kwargs(settings.database_url),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a request-scoped database session.

    The session is committed on success and rolled back on any exception, then
    always closed. Services therefore never manage transaction boundaries
    themselves; they operate within the unit of work provided here.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
