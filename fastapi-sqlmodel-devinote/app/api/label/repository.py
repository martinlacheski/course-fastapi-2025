
from app.api.label.model import NoteLabelLink
from sqlmodel import Session, select, delete
from app.api.label.model import Label, LabelRead
from app.api.share.model import LabelShare
from app.services.pagination import paginate_query
from typing import Optional


# Repositorio de etiquetas
class LabelRepository:

    # Inicialización de la sesión de la base de datos
    def __init__(self, db: Session):
        self.db = db

    # Listar las etiquetas de un usuario
    def list_by_user(self, owner_id: int) -> list[Label]:
        # Se retorna la lista de etiquetas
        query = select(Label).where(
            Label.owner_id == owner_id).order_by(
                Label.name.asc())  # type: ignore
        return self.db.exec(query).all()  # type: ignore

    # Obtiene una etiqueta por su ID
    def get(self, label_id: int) -> Label | None:
        # Se retorna la etiqueta
        return self.db.get(Label, label_id)

    # Obtiene una etiqueta por su nombre
    def get_by_name(self, owner_id: int, name: str) -> Label | None:
        # Se retorna la etiqueta
        query = select(Label).where(Label.owner_id ==
                                    owner_id, Label.name == name)
        return self.db.exec(query).first()

    # Obtiene una lista de etiquetas
    def list(
            self,
            search: Optional[str],  # type: ignore
            order_by: str,
            direction: str,
            page: int,
            per_page: int
    ):

        # Se retorna la lista de notas
        query = select(Label)

        # Se retorna la lista de notas filtrada por la búsqueda
        if search:
            query = query.where(Label.name.startswith(search))

        # Se definen los ordenamientos permitidos en la paginación
        allowed_order = {
            "id": Label.id,
            "name": Label.name.lower(),
        }

        # Se ejecuta la query con la paginación
        result = paginate_query(
            db=self.db,
            model=Label,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        # Se mapea la query a LabelRead para que la respuesta sea un JSON
        result["items"] = [LabelRead.model_validate(
            item) for item in result["items"]]

        # Se retorna el resultado
        return result

    # Crea una etiqueta
    def create(self, owner_id: int, name: str) -> Label:
        label = Label(owner_id=owner_id, name=name)
        self.db.add(label)
        self.db.commit()
        self.db.refresh(label)
        return label

    # Elimina una etiqueta
    def delete(self, label: Label) -> None:
        self.db.exec(delete(NoteLabelLink).where(
            NoteLabelLink.label_id == label.id))  # type: ignore
        self.db.exec(delete(LabelShare).where(
            LabelShare.label_id == label.id))  # type: ignore
        self.db.delete(label)
        self.db.commit()

    # Obtiene una lista de IDs de etiquetas para un usuario

    # def list_ids_for_owner_subset(self, owner_id: int,
    #                               ids: list[int]) -> list[int]:  # type: ignore
    #     # Si no hay IDs, retorna una lista vacía
    #     if not ids:
    #         return []

    #     # Retorna una lista de IDs de etiquetas para un usuario
    #     return self.db.exec(
    #         select(Label.id).where(Label.owner_id ==
    #                                owner_id,
    #                                Label.id.in_(set(ids)))  # type: ignore
    #     ).all()

    # # Obtiene una lista de IDs de etiquetas para una nota
    # def list_label_ids_for_note(self,
    #                             note_id: int) -> list[int]:  # type: ignore
    #     # Retorna una lista de IDs de etiquetas para una nota
    #     return self.db.exec(
    #         select(NoteLabelLink.label_id).where(
    #             NoteLabelLink.note_id == note_id)  # type: ignore
    #     ).all()

    # # Obtiene una lista de IDs de notas para una etiqueta
    # def list_note_ids_by_label_ids(self,
    #                                label_ids: list[int]) -> list[int]:  # type: ignore
    #     # Si no hay IDs, retorna una lista vacía
    #     if not label_ids:
    #         return []

    #     # Retorna una lista de IDs de notas para una etiqueta
    #     return self.db.exec(
    #         select(NoteLabelLink.note_id).where(
    #             NoteLabelLink.label_id.in_(label_ids))  # type: ignore
    #     ).all()
