
from fastapi import HTTPException, status
from sqlmodel import Session

from app.api.label.model import Label, LabelCreate
from app.api.label.repository import LabelRepository


class LabelService:

    # Inicialización de la clase
    def __init__(self, db: Session):
        self.repo = LabelRepository(db)

        ### Permisos ###

    # Permisos de lectura

    def user_can_read(self, user_id: int, label: Label) -> bool:

        # Si el usuario es el dueño de la nota
        if label.owner_id == user_id:
            return True

        # Si el usuario tiene permiso de lectura directo
        if self.shares.has_note_share(note_id=label.id, user_id=user_id):
            return True

        # Si el usuario tiene permiso de lectura por etiqueta
        label_ids = self.labels.list_label_ids_for_note(label.id)

        # Se verifica que el usuario tenga permiso de lectura por etiqueta
        return self.shares.has_any_label_share(label_ids=label_ids, user_id=user_id)

    # Permisos de edición
    def user_can_edit(self, user_id: int, label: Label) -> bool:

        # Si el usuario es el dueño de la nota
        if label.owner_id == user_id:
            return True

        # Si el usuario tiene permiso de edición directo
        if self.shares.has_note_share(note_id=label.id, user_id=user_id, role=ShareRole.EDIT):
            return True

        # Si el usuario tiene permiso de edición por etiqueta
        label_ids = self.labels.list_label_ids_for_note(label.id)

        # Se verifica que el usuario tenga permiso de edición por etiqueta
        return self.shares.has_any_label_share(label_ids=label_ids, user_id=user_id, role=ShareRole.EDIT)

    # Permisos de eliminación
    def user_can_delete(self, user_id: int, label: Label) -> bool:

        # Si el usuario es el dueño de la nota
        if label.owner_id == user_id:
            return True

        # Si el usuario tiene permiso de eliminación directo
        if self.shares.has_note_share(note_id=label.id, user_id=user_id, role=ShareRole.DELETE):
            return True

        # Si el usuario tiene permiso de eliminación por etiqueta
        label_ids = self.labels.list_label_ids_for_note(label.id)

        # Se verifica que el usuario tenga permiso de eliminación por etiqueta
        return self.shares.has_any_label_share(label_ids=label_ids, user_id=user_id, role=ShareRole.DELETE)

    ### CRUD ###

    # Listar etiquetas
    def list_labels(self, owner_id: int) -> list[Label]:
        # Se retornan todas las etiquetas del usuario
        return self.repo.list_by_user(owner_id)

    # Obtener una etiqueta
    def get_label(self, user_id: int, label_id: int) -> Label:

        # Se obtiene la etiqueta
        label = self.repo.get(label_id)

        # Se verifica que la etiqueta exista y que el usuario tenga autorización
        if not label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta no encontrada")
        if not self.user_can_read(user_id, label):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No se posee autorización")

        # Se retorna la etiqueta
        return label

    # Crear etiqueta
    def create(self, owner_id: int, payload: LabelCreate) -> Label:
        # Se verifica si la etiqueta ya existe y se lanza una excepción si es el caso
        if self.repo.get_by_name(owner_id, payload.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="La etiqueta ya existe")

        # Se retorna la etiqueta creada
        return self.repo.create(owner_id, payload.name)

    # Editar etiqueta
    def update(self, owner_id: int, label_id: int, payload: LabelCreate) -> Label:
        # Se verifica si la etiqueta existe y se lanza una excepción si es el caso
        label = self.repo.get(label_id)
        if not label or label.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="La etiqueta no existe o no posee autorización")

        # Se verifica si la etiqueta ya existe y se lanza una excepción si es el caso
        if self.repo.get_by_name(owner_id, payload.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="La etiqueta ya existe")

        # Se retorna la etiqueta editada
        return self.repo.update(owner_id, label_id, payload.name)

    # Eliminar etiqueta
    def delete(self, owner_id: int, label_id: int) -> None:
        # Se verifica si la etiqueta existe y se lanza una excepción si es el caso
        label = self.repo.get(label_id)
        if not label or label.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="La etiqueta no existe o no posee autorización")

        # Se elimina la etiqueta
        self.repo.delete(label)
