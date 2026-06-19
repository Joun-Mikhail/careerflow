"""Attachment endpoints: upload, list, secure download, and delete."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, Response, UploadFile, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.models.enums import AttachmentKind
from app.schemas.attachment import AttachmentRead
from app.services.attachment import AttachmentService

settings = get_settings()

router = APIRouter(tags=["attachments"])


@router.get(
    "/applications/{application_id}/attachments",
    response_model=list[AttachmentRead],
    summary="List attachments for an application",
)
def list_attachments(
    application_id: UUID, current_user: CurrentUser, db: DbSession
) -> list[AttachmentRead]:
    items = AttachmentService(db).list_for_application(current_user, application_id)
    return [AttachmentRead.model_validate(item) for item in items]


@router.post(
    "/applications/{application_id}/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an attachment for an application",
)
def upload_attachment(
    application_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File(description="Document to upload (PDF or DOCX).")],
    kind: Annotated[AttachmentKind, Form(description="Document category.")] = (
        AttachmentKind.OTHER
    ),
) -> AttachmentRead:
    # Read at most one byte beyond the limit so oversized uploads are rejected
    # without buffering the entire (potentially huge) payload.
    content = file.file.read(settings.max_upload_size_bytes + 1)
    attachment = AttachmentService(db).create(
        current_user,
        application_id,
        content=content,
        original_filename=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        kind=kind,
    )
    return AttachmentRead.model_validate(attachment)


@router.get(
    "/attachments/{attachment_id}/download",
    summary="Download an attachment (owner only)",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def download_attachment(attachment_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    attachment, content = AttachmentService(db).read_bytes(current_user, attachment_id)
    return Response(
        content=content,
        media_type=attachment.content_type,
        headers={
            # Force download rather than inline rendering of active content.
            "Content-Disposition": f'attachment; filename="{attachment.original_filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete(
    "/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an attachment",
)
def delete_attachment(attachment_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    AttachmentService(db).delete(current_user, attachment_id)
