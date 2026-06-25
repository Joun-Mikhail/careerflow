"""Certificate service — upload, list, download, and manage certificates."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ensure_found
from app.core.storage import FileStorage, get_storage
from app.core.uploads import CERTIFICATE_CONTENT_TYPES, validate_upload
from app.models.certificate import Certificate
from app.models.user import User
from app.repositories.certificate import CertificateRepository
from app.schemas.certificate import CertificateUpdate


class CertificateService:
    """Coordinates certificate metadata and optional file storage."""

    def __init__(self, session: Session, storage: FileStorage | None = None) -> None:
        self.repo = CertificateRepository(session)
        self.storage = storage or get_storage()

    def list_all(self, owner: User) -> list[Certificate]:
        return self.repo.list_for_user(owner.id)

    def get(self, owner: User, certificate_id: UUID) -> Certificate:
        return ensure_found(self.repo.get(owner.id, certificate_id), "Certificate not found.")

    def create(
        self,
        owner: User,
        *,
        name: str,
        issuer: str | None = None,
        issued_on: date | None = None,
        credential_url: str | None = None,
        content: bytes | None = None,
        original_filename: str | None = None,
        content_type: str | None = None,
    ) -> Certificate:
        certificate = Certificate(
            user_id=owner.id,
            name=name[:200],
            issuer=issuer,
            issued_on=issued_on,
            credential_url=credential_url,
        )
        # An uploaded proof file is optional.
        if content:
            suffix = validate_upload(content, content_type or "", CERTIFICATE_CONTENT_TYPES)
            certificate.stored_filename = self.storage.save(
                content, suffix=suffix, content_type=content_type
            )
            certificate.original_filename = (original_filename or "certificate")[:255]
            certificate.content_type = content_type
            certificate.size_bytes = len(content)
        return self.repo.add(certificate)

    def read_bytes(self, owner: User, certificate_id: UUID) -> tuple[Certificate, bytes]:
        certificate = self.get(owner, certificate_id)
        if not certificate.stored_filename or not self.storage.exists(certificate.stored_filename):
            raise NotFoundError("This certificate has no downloadable file.")
        return certificate, self.storage.read(certificate.stored_filename)

    def update(self, owner: User, certificate_id: UUID, data: CertificateUpdate) -> Certificate:
        certificate = self.get(owner, certificate_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(certificate, field, value)
        self.repo.flush()
        return certificate

    def delete(self, owner: User, certificate_id: UUID) -> None:
        certificate = self.get(owner, certificate_id)
        if certificate.stored_filename:
            self.storage.delete(certificate.stored_filename)
        self.repo.delete(certificate)
