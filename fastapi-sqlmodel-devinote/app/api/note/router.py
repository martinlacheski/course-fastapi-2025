from fastapi import APIRouter, status
from sqlmodel import Session

from app.core.dependencies import CurrentUser, DBSession
from app.api.note.model import Note, NoteCreate, NoteRead, NoteUpdate
from app.api.note.service import NoteService
from app.api.label.repository import LabelRepository

router = APIRouter(prefix="/notes", tags=["Notes"])


# Helper para armar NoteRead con label_ids desde la tabla puente
def _note_to_read(db: Session, note: Note) -> NoteRead:
    label_repo = LabelRepository(db)
    raw_ids = label_repo.list_label_ids_for_note(note.id)

    # Por si el repo devuelve [(1,), (2,), ...]
    label_ids = [lid[0] if isinstance(lid, tuple) else lid for lid in raw_ids]

    return NoteRead.model_validate(
        note,
        update={"label_ids": label_ids},
    )


@router.get("/", response_model=list[NoteRead])
def list_notes(db: DBSession, user: CurrentUser):
    service = NoteService(db)
    notes = service.list_notes(user.id)
    return [_note_to_read(db, note) for note in notes]


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: DBSession, user: CurrentUser):
    service = NoteService(db)
    note = service.get_note(user.id, note_id)
    return _note_to_read(db, note)


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: DBSession, user: CurrentUser):
    service = NoteService(db)
    note = service.create(user.id, payload)
    return _note_to_read(db, note)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: DBSession, user: CurrentUser):
    service = NoteService(db)
    note = service.update(user.id, note_id, payload)
    return _note_to_read(db, note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: DBSession, user: CurrentUser):
    NoteService(db).delete(user.id, note_id)
    return None
