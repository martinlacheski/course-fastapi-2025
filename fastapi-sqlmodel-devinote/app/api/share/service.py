
from fastapi import HTTPException, status
from sqlmodel import Session

from app.api.share.model import ShareRole
from app.api.label.repository import LabelRepository
from app.api.note.repository import NoteRepository
from app.api.share.repository import ShareRepository


class ShareService:

    # Inicialización de la clase
    def __init__(self, db: Session):
        # Inicialización de los repositorios
        self.shares = ShareRepository(db)
        self.notes = NoteRepository(db)
        self.labels = LabelRepository(db)

    # Metodo para compartir una nota
    def share_note(self, owner_id: int, note_id: int, target_user_id: int, role: ShareRole):

        # Se obtiene la nota
        note = self.notes.get(note_id)

        # Se verifica que la nota exista y que el usuario tenga autorización
        if not note or note.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada o no autorizado")

        # Se crea o actualiza el share
        share = self.shares.upsert_note_share(
            note_id, target_user_id, role.value if hasattr(role, "value") else role)

        # Se retorna el share
        return share

    # Metodo para quitar la compartición de una nota
    def unshare_note(self, owner_id: int, note_id: int, target_user_id: int):

        # Se obtiene la nota
        note = self.notes.get(note_id)

        # Se verifica que la nota exista y que el usuario tenga autorización
        if not note or note.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada o no posee autorización")

        # Se quita la compartición de la nota
        self.shares.remove_note_share(note_id, target_user_id)

    # Metodo para compartir una etiqueta
    def share_label(self, owner_id: int, label_id: int, target_user_id: int, role: ShareRole):

        # Se obtiene la etiqueta
        label = self.labels.get(label_id)

        # Se verifica que la etiqueta exista y que el usuario tenga autorización
        if not label or label.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta no encontrada o no posee autorización")

        # Se crea o actualiza el share
        share = self.shares.upsert_label_share(
            label_id, target_user_id, role.value if hasattr(role, "value") else role)

        # Se retorna el share
        return share

    # Metodo para quitar la compartición de una etiqueta
    def unshare_label(self, owner_id: int, label_id: int, target_user_id: int):

        # Se obtiene la etiqueta
        label = self.labels.get(label_id)

        # Se verifica que la etiqueta exista y que el usuario tenga autorización
        if not label or label.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta no encontrada o no posee autorización")

        # Se quita la compartición de la etiqueta
        self.shares.remove_label_share(label_id, target_user_id)
