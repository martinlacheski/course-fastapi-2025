

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DBSession
from app.api.label.model import LabelCreate, LabelRead
from app.api.label.service import LabelService


router = APIRouter(prefix="/labels", tags=["Labels"])


# listar etiquetas
@router.get("/", response_model=list[LabelRead])
def list_labels(db: DBSession, user: CurrentUser):
    return LabelService(db).list_labels(user.id)


# Obtener una etiqueta
@router.get("/{label_id}", response_model=LabelRead)
def get_label(label_id: int, db: DBSession, user: CurrentUser):
    return LabelService(db).get_label(user.id, label_id)


# Crear etiqueta
@router.post("/", response_model=LabelRead, status_code=status.HTTP_201_CREATED)
def create_label(payload: LabelCreate, db: DBSession, user: CurrentUser):
    return LabelService(db).create(user.id, payload)


# Editar etiqueta
@router.patch("/{label_id}", response_model=LabelRead)
def update_label(label_id: int, payload: LabelCreate, db: DBSession, user: CurrentUser):
    return LabelService(db).update(user.id, label_id, payload)


# Borrar etiqueta
@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(label_id: int, db: DBSession, user: CurrentUser):
    LabelService(db).delete(user.id, label_id)
    return None
