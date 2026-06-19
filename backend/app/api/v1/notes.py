"""Note endpoints, nested under applications and addressable directly."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.services.note import NoteService

router = APIRouter(tags=["notes"])


@router.get(
    "/applications/{application_id}/notes",
    response_model=list[NoteRead],
    summary="List notes for an application",
)
def list_notes(application_id: UUID, current_user: CurrentUser, db: DbSession) -> list[NoteRead]:
    notes = NoteService(db).list_for_application(current_user, application_id)
    return [NoteRead.model_validate(item) for item in notes]


@router.post(
    "/applications/{application_id}/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note for an application",
)
def create_note(
    application_id: UUID, data: NoteCreate, current_user: CurrentUser, db: DbSession
) -> NoteRead:
    note = NoteService(db).create(current_user, application_id, data)
    return NoteRead.model_validate(note)


@router.patch("/notes/{note_id}", response_model=NoteRead, summary="Update a note")
def update_note(
    note_id: UUID, data: NoteUpdate, current_user: CurrentUser, db: DbSession
) -> NoteRead:
    return NoteRead.model_validate(NoteService(db).update(current_user, note_id, data))


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a note")
def delete_note(note_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    NoteService(db).delete(current_user, note_id)
