
from app.services.pagination import paginate_query
from typing import Any, Optional, Sequence
from sqlmodel import Session, select, delete, desc

from app.api.label.model import NoteLabelLink
from app.api.note.model import Note, NoteRead


# Repositorio de notas
class NoteRepository:

    # Inicialización de la sesión de la base de datos
    def __init__(self, db: Session):
        self.db = db

    # Obtiene una lista de notas
    def list_owned(self, owner_id: int) -> Sequence[Note]:
        # Se genera la query de notas ordenadas por Usuario
        query = (
            select(Note)
            .where(Note.owner_id == owner_id)
            .order_by(desc(Note.id))
        )
        # Se retorna la lista de notas
        return self.db.exec(query).all()

    # Obtiene una nota por su ID
    def get(self, note_id: int) -> Note | None:
        # Se retorna la nota
        return self.db.get(Note, note_id)

    # Obtiene una lista de notas
    def list(
            self,
            search: Optional[str],
            order_by: str,
            direction: str,
            page: int,
            per_page: int
    ):

        # Se retorna la lista de notas
        query = select(Note)

        # Se retorna la lista de notas filtrada por la búsqueda
        if search:
            query = query.where(Note.title.startswith(search))

        # Se definen los ordenamientos permitidos en la paginación
        allowed_order = {
            "id": Note.id,
            "title": Note.title.lower(),
        }

        # Se ejecuta la query con la paginación
        result = paginate_query(
            db=self.db,
            model=Note,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        # Se mapea la query a NoteRead para que la respuesta sea un JSON
        result["items"] = [NoteRead.model_validate(
            item) for item in result["items"]]

        # Se retorna el resultado
        return result

    # Crea una nota
    def create(self, note: Note) -> Note:
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    # Actualiza una nota
    def update(self, note: Note) -> Note:
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    # Elimina una nota
    def delete(self, note: Note) -> None:
        self.db.exec(delete(NoteLabelLink).where(
            NoteLabelLink.note_id == note.id))  # type: ignore
        self.db.delete(note)
        self.db.commit()

    # # Reemplaza las etiquetas de una nota
    # def replace_labels(self, owner_id: int, note_id: int, label_ids: list[int]) -> None:
    #     # Se eliminan las etiquetas de la nota
    #     self.db.exec(delete(NoteLabelLink).where(
    #         NoteLabelLink.note_id == note_id))  # type: ignore

    #     # Se agregan las nuevas etiquetas
    #     for label in set(label_ids or []):
    #         self.db.add(NoteLabelLink(note_id=note_id, label_id=label))

    #     # Se commitea la transacción
    #     self.db.commit()

    # # Obtiene una lista de notas por IDs
    # def list_by_ids(self, ids: list[int]) -> list[Note]:
    #     # Si no hay IDs, retorna una lista vacía
    #     if not ids:
    #         return []

    #     # Se retorna la lista de notas
    #     return self.db.exec(select(Note).where(Note.id.in_(ids))).all()
