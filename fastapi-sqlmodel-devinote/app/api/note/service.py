

from fastapi import HTTPException, status
from sqlmodel import Session

from app.api.note.model import Note, NoteCreate, NoteUpdate
from app.api.share.model import ShareRole
from app.api.label.repository import LabelRepository
from app.api.note.repository import NoteRepository
from app.api.share.repository import ShareRepository


class NoteService:

    # Inicialización de la clase
    def __init__(self, db: Session):

        # Inicialización de la sesión de la base de datos
        self.db = db
        # Inicialización de los repositorios
        self.notes = NoteRepository(db)
        self.labels = LabelRepository(db)
        self.shares = ShareRepository(db)

    # Helper: arma el Note con los label_ids
    def _note_to_read(self, note: Note) -> NoteCreate:
        raw_ids = self.labels.list_label_ids_for_note(note.id)

        # Por si el repositorio devuelve tuplas (ej: [(1,), (2,)])
        label_ids = [lid[0] if isinstance(
            lid, tuple) else lid for lid in raw_ids]

        return NoteCreate.model_validate(
            note,
            update={"label_ids": label_ids},
        )

    ### Permisos ###

    # Permisos de lectura

    def user_can_read(self, user_id: int, note: Note) -> bool:

        # Si el usuario es el dueño de la nota
        if note.owner_id == user_id:
            return True

        # Si el usuario tiene permiso de lectura directo
        if self.shares.has_note_share(note_id=note.id, user_id=user_id):
            return True

        # Si el usuario tiene permiso de lectura por etiqueta
        label_ids = self.labels.list_label_ids_for_note(note.id)

        # Se verifica que el usuario tenga permiso de lectura por etiqueta
        return self.shares.has_any_label_share(label_ids=label_ids, user_id=user_id)

    # Permisos de edición
    def user_can_edit(self, user_id: int, note: Note) -> bool:

        # Si el usuario es el dueño de la nota
        if note.owner_id == user_id:
            return True

        # Si el usuario tiene permiso de edición directo
        if self.shares.has_note_share(note_id=note.id, user_id=user_id, role=ShareRole.EDIT):
            return True

        # Si el usuario tiene permiso de edición por etiqueta
        label_ids = self.labels.list_label_ids_for_note(note.id)

        # Se verifica que el usuario tenga permiso de edición por etiqueta
        return self.shares.has_any_label_share(label_ids=label_ids, user_id=user_id, role=ShareRole.EDIT)

    # Permisos de eliminación
    def user_can_delete(self, user_id: int, note: Note) -> bool:

        # Si el usuario es el dueño de la nota
        if note.owner_id == user_id:
            return True

        # Si el usuario tiene permiso de eliminación directo
        if self.shares.has_note_share(note_id=note.id, user_id=user_id, role=ShareRole.DELETE):
            return True

        # Si el usuario tiene permiso de eliminación por etiqueta
        label_ids = self.labels.list_label_ids_for_note(note.id)

        # Se verifica que el usuario tenga permiso de eliminación por etiqueta
        return self.shares.has_any_label_share(label_ids=label_ids, user_id=user_id, role=ShareRole.DELETE)

    ### CRUD ###

    # Lista de notas

        # Lista de notas
    def list_notes(self, user_id: int) -> list[NoteCreate]:

        # Lista de notas propias
        owned = self.notes.list_owned(user_id)

        # Lista de notas compartidas directamente
        direct_ids = self.shares.list_note_ids_shared_directly(user_id)

        # Lista de notas compartidas por etiqueta
        shared_label_ids = self.shares.list_label_ids_shared_with_user(user_id)
        ids_by_label = self.labels.list_note_ids_by_label_ids(shared_label_ids)

        # Lista de notas compartidas
        combined_ids = list({*direct_ids, *ids_by_label})
        shared = self.notes.list_by_ids(combined_ids)

        # Lista combinada sin duplicados
        combined = {note.id: note for note in owned}
        for note in shared:
            combined.setdefault(note.id, note)

        # Lista ordenada
        all_notes = sorted(
            combined.values(),
            key=lambda note: note.id,
            reverse=True
        )

        # Devolvemos NoteCreate con label_ids
        return [self._note_to_read(note) for note in all_notes]

    # Obtener una nota

    def get_note(self, user_id: int, note_id: int) -> Note:

        # Se obtiene la nota
        note = self.notes.get(note_id)

        # Se verifica que la nota exista y que el usuario tenga autorización
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")
        if not self.user_can_read(user_id, note):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No se posee autorización")

        # Se retorna la nota
        return self._note_to_read(note)

    # Crear una nota
    def create(self, owner_id: int, payload: NoteCreate) -> Note:

        # Se crea la nota
        note = self.notes.create(
            Note(owner_id=owner_id, **
                 payload.model_dump(exclude={"label_ids"}))
        )

        # Se agregan las etiquetas con la funcion helper
        if payload.label_ids:
            self._set_labels(owner_id, note.id, payload.label_ids)

        # Se retorna la nota
        return note

    # Actualizar una nota
    def update(self, user_id: int, note_id: int, payload: NoteUpdate) -> Note:

        # Se obtiene la nota
        note = self.notes.get(note_id)

        # Se verifica que la nota exista y que el usuario tenga autorización
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")
        if not self.user_can_edit(user_id, note):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No se posee autorización")

        # Se actualizan los datos de la nota
        updates = payload.model_dump(exclude_none=True)
        label_ids = updates.pop("label_ids", None)

        # Se actualizan los datos de la nota
        for key, value in updates.items():
            setattr(note, key, value)

        # Se actualiza la nota
        note = self.notes.update(note)

        # Se agregan las etiquetas con la funcion helper si es necesario
        if label_ids is not None:
            if note.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="No existe o no posee autorización")
            self._set_labels(user_id, note.id, label_ids)

        # Se retorna la nota
        return self._note_to_read(note)

    # Eliminar una nota
    def delete(self, user_id: int, note_id: int) -> None:

        # Se obtiene la nota
        note = self.notes.get(note_id)

        # Se verifica que la nota exista y que el usuario tenga autorización
        if not note or note.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No existe la nota o no posee autorización")

        # Se elimina la nota
        self.notes.delete(note)

    # helper para agregar etiquetas
    def _set_labels(self, owner_id: int, note_id: int, label_ids: list[int]) -> None:

        # Se verifica que las etiquetas existan
        valid_ids = self.labels.list_ids_for_owner_subset(
            owner_id, label_ids or [])

        # Se agregan las etiquetas con la funcion de replace_labels para evitar errores
        self.notes.replace_labels(owner_id, note_id, valid_ids)
