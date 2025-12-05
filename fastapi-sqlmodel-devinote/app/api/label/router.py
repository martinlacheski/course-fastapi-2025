

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DBSession
from app.api.label.model import LabelCreate, LabelRead
from app.api.label.service import LabelService


router = APIRouter(prefix="/labels", tags=["Labels"])


# listar etiquetas
@router.get("/", response_model=list[LabelRead])
def list_labels(db: DBSession, user: CurrentUser):
    return LabelService(db).list(user.id)


# Crear etiqueta
@router.post("/", response_model=LabelRead, status_code=status.HTTP_201_CREATED)
def create_label(payload: LabelCreate, db: DBSession, user: CurrentUser):
    return LabelService(db).create(user.id, payload)


# Borrar etiqueta
@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(label_id: int, db: DBSession, user: CurrentUser):
    LabelService(db).delete(user.id, label_id)
    return None
