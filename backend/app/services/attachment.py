"""Attachment service — validation, storage, and retrieval of documents."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.core.storage import LocalFileStorage
from app.models.attachment import Attachment
from app.models.enums import AttachmentKind
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.attachment import AttachmentRepository

settings = get_settings()

# Allow-list of accepted document types mapped to their canonical extension.
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


class AttachmentService:
    """Coordinates attachment validation, storage, and metadata."""

    def __init__(self, session: Session, storage: LocalFileStorage | None = None) -> None:
        self.repo = AttachmentRepository(session)
        self.applications = ApplicationRepository(session)
        self.storage = storage or LocalFileStorage()

    def list_for_application(self, owner: User, application_id: UUID) -> list[Attachment]:
        self._ensure_application_owned(owner, application_id)
        return self.repo.list_for_application(owner.id, application_id)

    def create(
        self,
        owner: User,
        application_id: UUID,
        *,
        content: bytes,
        original_filename: str,
        content_type: str,
        kind: AttachmentKind,
    ) -> Attachment:
        self._ensure_application_owned(owner, application_id)
        self._validate(content, content_type)

        suffix = ALLOWED_CONTENT_TYPES[content_type]
        stored_filename = self.storage.save(content, suffix=suffix)
        attachment = Attachment(
            user_id=owner.id,
            application_id=application_id,
            kind=kind,
            original_filename=original_filename[:255],
            stored_filename=stored_filename,
            content_type=content_type,
            size_bytes=len(content),
        )
        return self.repo.add(attachment)

    def get(self, owner: User, attachment_id: UUID) -> Attachment:
        attachment = self.repo.get(owner.id, attachment_id)
        if attachment is None:
            raise NotFoundError("Attachment not found.")
        return attachment

    def read_bytes(self, owner: User, attachment_id: UUID) -> tuple[Attachment, bytes]:
        attachment = self.get(owner, attachment_id)
        if not self.storage.exists(attachment.stored_filename):
            raise NotFoundError("Attachment file is missing.")
        return attachment, self.storage.read(attachment.stored_filename)

    def delete(self, owner: User, attachment_id: UUID) -> None:
        attachment = self.get(owner, attachment_id)
        self.storage.delete(attachment.stored_filename)
        self.repo.delete(attachment)

    def _validate(self, content: bytes, content_type: str) -> None:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                "Unsupported file type. Allowed types: PDF, DOCX.",
                details={"allowed": sorted(ALLOWED_CONTENT_TYPES)},
            )
        if not content:
            raise ValidationError("Uploaded file is empty.")
        if len(content) > settings.max_upload_size_bytes:
            raise ValidationError(
                "File exceeds the maximum allowed size.",
                details={"max_bytes": settings.max_upload_size_bytes},
            )

    def _ensure_application_owned(self, owner: User, application_id: UUID) -> None:
        if self.applications.get(owner.id, application_id) is None:
            raise NotFoundError("Application not found.")
