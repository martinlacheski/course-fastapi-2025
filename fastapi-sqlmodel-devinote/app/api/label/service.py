
from fastapi import HTTPException, status
from sqlmodel import Session

from app.api.label.model import Label, LabelCreate
from app.api.label.repository import LabelRepository


class LabelService:

    # Inicialización de la clase
    def __init__(self, db: Session):
        self.repo = LabelRepository(db)

    # Listar etiquetas
    def list(self, owner_id: int) -> list[Label]:
        # Se retornan todas las etiquetas del usuario
        return self.repo.list_by_user(owner_id)

    # Crear etiqueta
    def create(self, owner_id: int, payload: LabelCreate) -> Label:
        # Se verifica si la etiqueta ya existe y se lanza una excepción si es el caso
        if self.repo.get_by_name(owner_id, payload.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="La etiqueta ya existe")

        # Se retorna la etiqueta creada
        return self.repo.create(owner_id, payload.name)

    # Eliminar etiqueta
    def delete(self, owner_id: int, label_id: int) -> None:
        # Se verifica si la etiqueta existe y se lanza una excepción si es el caso
        label = self.repo.get(label_id)
        if not label or label.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="La etiqueta no existe o no posee autorización")

        # Se elimina la etiqueta
        self.repo.delete(label)
