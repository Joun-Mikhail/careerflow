"""CV endpoints: upload, list, download, rename/default, delete."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, Response, UploadFile, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.schemas.cv import CvRead, CvUpdate
from app.services.cv import CvService

settings = get_settings()

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("", response_model=list[CvRead], summary="List the current user's CVs")
def list_cvs(current_user: CurrentUser, db: DbSession) -> list[CvRead]:
    return [CvRead.model_validate(item) for item in CvService(db).list_all(current_user)]


@router.post(
    "",
    response_model=CvRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a CV (PDF or DOCX)",
)
def upload_cv(
    current_user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File(description="CV document (PDF or DOCX).")],
    title: Annotated[str | None, Form(description="Optional display title.")] = None,
    make_default: Annotated[bool, Form(description="Mark this CV as the default.")] = False,
) -> CvRead:
    content = file.file.read(settings.max_upload_size_bytes + 1)
    cv = CvService(db).create_upload(
        current_user,
        content=content,
        original_filename=file.filename or "cv",
        content_type=file.content_type or "application/octet-stream",
        title=title,
        make_default=make_default,
    )
    return CvRead.model_validate(cv)


@router.get(
    "/{cv_id}/download",
    summary="Download a CV file (owner only)",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def download_cv(cv_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    cv, content = CvService(db).read_bytes(current_user, cv_id)
    return Response(
        content=content,
        media_type=cv.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{cv.original_filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.patch("/{cv_id}", response_model=CvRead, summary="Rename a CV or set it as default")
def update_cv(cv_id: UUID, data: CvUpdate, current_user: CurrentUser, db: DbSession) -> CvRead:
    return CvRead.model_validate(CvService(db).update(current_user, cv_id, data))


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a CV")
def delete_cv(cv_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    CvService(db).delete(current_user, cv_id)
