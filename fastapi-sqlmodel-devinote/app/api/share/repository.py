
from sqlmodel import Session, select, delete

from app.api.share.model import LabelShare, NoteShare


# Repositorio de comparticiones de notas y etiquetas
class ShareRepository:

    # Inicialización de la sesión de la base de datos
    def __init__(self, db: Session):
        self.db = db

    # Compartir una nota con un usuario
    def upsert_note_share(self, note_id: int, user_id: int, role: str) -> NoteShare:
        # Busca si ya existe una compartición
        share = self.db.exec(
            select(NoteShare).where(NoteShare.note_id == note_id, NoteShare.user_id == user_id)).first()

        # Si existe, actualiza el rol y retorna la compartición
        if share:
            share.role = role
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            return share

        # Si no existe, crea y retorna una nueva compartición
        share = NoteShare(note_id=note_id, user_id=user_id, role=role)
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    # Eliminar una compartición de una nota
    def remove_note_share(self, note_id: int, user_id: int) -> None:
        # Elimina la compartición
        self.db.exec(delete(NoteShare).where(NoteShare.note_id ==
                     note_id, NoteShare.user_id == user_id))
        # Commit para guardar los cambios
        self.db.commit()

    # Compartir una etiqueta con un usuario
    def upsert_label_share(self, label_id: int, user_id: int, role: str) -> LabelShare:
        # Busca si ya existe una compartición
        share = self.db.exec(
            select(LabelShare).where(LabelShare.label_id == label_id, LabelShare.user_id == user_id)).first()

        # Si existe, actualiza el rol y retorna la compartición
        if share:
            share.role = role
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            return share

        # Si no existe, crea y retorna una nueva compartición
        share = LabelShare(label_id=label_id, user_id=user_id, role=role)
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    # Eliminar una compartición de una etiqueta
    def remove_label_share(self, label_id: int, user_id: int) -> None:
        # Elimina la compartición
        self.db.exec(delete(LabelShare).where(LabelShare.label_id ==
                     label_id, LabelShare.user_id == user_id))
        # Commit para guardar los cambios
        self.db.commit()

    # Verificar si un usuario tiene una compartición de una nota
    def has_note_share(self, note_id: int, user_id: int, role: str | None = None) -> bool:
        # Busca si el usuario tiene una compartición de la nota
        query = select(NoteShare).where(
            NoteShare.note_id == note_id,
            NoteShare.user_id == user_id
        )

        # Si se especifica un rol, lo filtra
        if role is not None:
            query = query.where(NoteShare.role == role)

        # Retorna True si encuentra una compartición, False en caso contrario
        return self.db.exec(query).first() is not None

    # Verificar si un usuario tiene una compartición de una etiqueta
    def has_any_label_share(self, label_ids: list[int], user_id: int, role: str | None = None) -> bool:
        # Si no hay etiquetas, retorna False
        if not label_ids:
            return False

        # Busca si el usuario tiene alguna de las etiquetas compartidas
        query = select(LabelShare).where(
            LabelShare.label_id.in_(label_ids),
            LabelShare.user_id == user_id
        )

        # Si se especifica un rol, lo filtra
        if role is not None:
            query = query.where(LabelShare.role == role)

        # Retorna True si encuentra una compartición, False en caso contrario
        return self.db.exec(query).first() is not None

    # Listar las notas compartidas directamente con un usuario
    def list_note_ids_shared_directly(self, user_id: int) -> list[int]:
        # Retorna las notas compartidas directamente con el usuario
        return self.db.exec(
            select(NoteShare.note_id).where(NoteShare.user_id == user_id)
        ).all()

    # Listar las etiquetas compartidas con un usuario
    def list_label_ids_shared_with_user(self, user_id: int) -> list[int]:
        # Retorna las etiquetas compartidas con el usuario
        return self.db.exec(
            select(LabelShare.label_id).where(LabelShare.user_id == user_id)
        ).all()
