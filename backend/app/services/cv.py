"""CV service — upload, list, download, and manage CVs in the vault."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ensure_found
from app.core.logging import log_action
from app.core.storage import FileStorage, get_storage
from app.core.uploads import CV_CONTENT_TYPES, validate_upload
from app.models.cv import Cv
from app.models.enums import CvSource
from app.models.user import User
from app.repositories.cv import CvRepository
from app.schemas.cv import CvUpdate


class CvService:
    """Coordinates CV validation, storage, and metadata."""

    def __init__(self, session: Session, storage: FileStorage | None = None) -> None:
        self.repo = CvRepository(session)
        self.storage = storage or get_storage()

    def list_all(self, owner: User) -> list[Cv]:
        return self.repo.list_for_user(owner.id)

    def get(self, owner: User, cv_id: UUID) -> Cv:
        return ensure_found(self.repo.get(owner.id, cv_id), "CV not found.")

    def create_upload(
        self,
        owner: User,
        *,
        content: bytes,
        original_filename: str,
        content_type: str,
        title: str | None = None,
        make_default: bool = False,
    ) -> Cv:
        suffix = validate_upload(content, content_type, CV_CONTENT_TYPES)
        stored_filename = self.storage.save(content, suffix=suffix, content_type=content_type)

        # The first CV a user uploads becomes their default automatically.
        is_first = not self.repo.list_for_user(owner.id)
        if make_default or is_first:
            self.repo.clear_default(owner.id)

        cv = Cv(
            user_id=owner.id,
            title=(title or original_filename or "CV")[:200],
            source=CvSource.UPLOADED,
            is_default=make_default or is_first,
            original_filename=original_filename[:255],
            stored_filename=stored_filename,
            content_type=content_type,
            size_bytes=len(content),
        )
        self.repo.add(cv)
        log_action("cv_uploaded", status="created", user_id=owner.id, cv_id=str(cv.id))
        return cv

    def save_tailored(
        self,
        owner: User,
        *,
        title: str,
        content_text: str,
        parent_cv_id: UUID | None = None,
        job_id: UUID | None = None,
    ) -> Cv:
        """Persist an AI-tailored CV as a new text-backed version."""
        cv = Cv(
            user_id=owner.id,
            title=title[:200],
            source=CvSource.AI_TAILORED,
            content_text=content_text,
            parent_cv_id=parent_cv_id,
            job_id=job_id,
        )
        self.repo.add(cv)
        log_action("cv_tailored", status="created", user_id=owner.id, cv_id=str(cv.id))
        return cv

    def read_bytes(self, owner: User, cv_id: UUID) -> tuple[Cv, bytes]:
        cv = self.get(owner, cv_id)
        if not cv.stored_filename or not self.storage.exists(cv.stored_filename):
            raise NotFoundError("This CV has no downloadable file.")
        return cv, self.storage.read(cv.stored_filename)

    def update(self, owner: User, cv_id: UUID, data: CvUpdate) -> Cv:
        cv = self.get(owner, cv_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("is_default") is True:
            self.repo.clear_default(owner.id)
        for field, value in changes.items():
            setattr(cv, field, value)
        self.repo.flush()
        return cv

    def delete(self, owner: User, cv_id: UUID) -> None:
        cv = self.get(owner, cv_id)
        if cv.stored_filename:
            self.storage.delete(cv.stored_filename)
        self.repo.delete(cv)
