"""Certificate endpoints: create (with optional file), list, download, edit, delete."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, Response, UploadFile, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.schemas.certificate import CertificateRead, CertificateUpdate
from app.services.certificate import CertificateService

settings = get_settings()

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get(
    "", response_model=list[CertificateRead], summary="List the current user's certificates"
)
def list_certificates(current_user: CurrentUser, db: DbSession) -> list[CertificateRead]:
    items = CertificateService(db).list_all(current_user)
    return [CertificateRead.model_validate(item) for item in items]


@router.post(
    "",
    response_model=CertificateRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a certificate, optionally with an uploaded file",
)
def create_certificate(
    current_user: CurrentUser,
    db: DbSession,
    name: Annotated[str, Form(description="Certificate name.")],
    issuer: Annotated[str | None, Form()] = None,
    issued_on: Annotated[date | None, Form()] = None,
    credential_url: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File(description="Optional proof (PDF/DOCX/PNG/JPG).")] = (
        None
    ),
) -> CertificateRead:
    content = file.file.read(settings.max_upload_size_bytes + 1) if file is not None else None
    certificate = CertificateService(db).create(
        current_user,
        name=name,
        issuer=issuer,
        issued_on=issued_on,
        credential_url=credential_url,
        content=content,
        original_filename=file.filename if file is not None else None,
        content_type=file.content_type if file is not None else None,
    )
    return CertificateRead.model_validate(certificate)


@router.get(
    "/{certificate_id}/download",
    summary="Download a certificate file (owner only)",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def download_certificate(
    certificate_id: UUID, current_user: CurrentUser, db: DbSession
) -> Response:
    certificate, content = CertificateService(db).read_bytes(current_user, certificate_id)
    return Response(
        content=content,
        media_type=certificate.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{certificate.original_filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.patch(
    "/{certificate_id}", response_model=CertificateRead, summary="Edit certificate metadata"
)
def update_certificate(
    certificate_id: UUID,
    data: CertificateUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> CertificateRead:
    certificate = CertificateService(db).update(current_user, certificate_id, data)
    return CertificateRead.model_validate(certificate)


@router.delete(
    "/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a certificate",
)
def delete_certificate(certificate_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    CertificateService(db).delete(current_user, certificate_id)
