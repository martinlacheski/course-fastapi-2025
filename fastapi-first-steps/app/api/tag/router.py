
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from operator import ge

from app.api.tag.repository import TagRepository
from app.api.tag.schemas import TagCreate, TagPublic, TagUpdate
from app.core.db import get_db
from app.core.security import get_current_user

# Se crea el router para los endpoints de tags y se le asigna un prefijo y un tag para la documentación
router = APIRouter(prefix="/tags", tags=["Tags"])

########### Endpoints ###########


# Endpoint para obtener todos los tags
@router.get("/",
            response_model=dict
            )
# Búsqueda por nombre
async def list_tags(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order_by: str = Query("id", pattern="^(id|name)$"),
    direction: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    db: Session = Depends(get_db)
):
    repository = TagRepository(db)
    return repository.list_tags(page=page, per_page=per_page, order_by=order_by, direction=direction, search=search)


# Endpoint para obtener un tag por su ID
@router.get("/{tag_id}",
            response_model=TagPublic,
            response_description="Tag encontrado"
            )
# Path parameter para controlar el valor del ID del Tag
async def get_tag(tag_id: int = Path(
        ...,
        ge=1,
        title="ID del tag",
        description="Identificador del tag. Debe ser mayor o igual a 1",
        example=1),
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    # Se crea el repositorio
    repository = TagRepository(db)

    # Obtenemos el tag
    tag = repository.get_by_id(tag_id)

    # Si no se encuentra el tag, se lanza una excepción
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Se retorna el tag
    return tag


# Endpoint para crear una nueva etiqueta
@router.post("/",
             response_model=TagPublic,
             response_description="Etiqueta creada exitosamente",
             status_code=status.HTTP_201_CREATED
             )
# Crear una nueva etiqueta con validación de usuario autenticado
def create_tag(tag: TagCreate,
               # Se inyecta la sesión de la base de datos
               db: Session = Depends(get_db),
               # Se valida que el usuario este autenticado
               user=Depends(get_current_user)
               ):

    # Se crea el repositorio
    repository = TagRepository(db)

    # Se intenta crear el tag
    try:
        tag_created = repository.create_tag(
            name=tag.name
        )

        # Se guardan los cambios en la base de datos
        db.commit()

        # Se refresca el tag
        db.refresh(tag_created)

        # Se retorna el tag creado
        return tag_created

    # Si ocurre un error, se lanza una excepción
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Endpoint para actualizar una etiqueta
@router.put("/{tag_id}",
            response_model=TagPublic,
            response_description="Etiqueta actualizada exitosamente"
            )
# Actualizar una etiqueta con validación de usuario autenticado
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    # Se crea el repositorio
    repository = TagRepository(db)

    # Obtenemos el tag
    tag = repository.get_by_id(tag_id)

    # Si no se encuentra el tag, se lanza una excepción
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")

    # Se intenta actualizar el tag
    try:
        updates = payload.model_dump(exclude_unset=True)
        tag = repository.update(tag, updates)

        # Se guardan los cambios en la base de datos
        db.commit()

        # Se refresca el tag
        db.refresh(tag)

        # Se retorna el tag
        return tag

    # Si ocurre un error, se lanza una excepción
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Endpoint para eliminar una etiqueta
@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_tag(tag_id: int,
               # Se inyecta la sesión de la base de datos
               db: Session = Depends(get_db),
               # Se valida que el usuario este autenticado
               user=Depends(get_current_user)):

    # Se crea el repositorio
    repository = TagRepository(db)

    # Obtenemos el tag
    tag = repository.get_by_id(tag_id)

    # Si no se encuentra el tag, se lanza una excepción
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")

    # Se intenta eliminar el tag
    try:
        repository.delete(tag)

        # Se guardan los cambios en la base de datos
        db.commit()

    # Si ocurre un error, se lanza una excepción
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Endpoint para obtener la etiqueta mas popular
@router.get("/popular/top")
def get_most_popular_tag(
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    # Se crea el repositorio
    repository = TagRepository(db)

    # Se obtiene el tag mas popular
    row = repository.most_popular()

    # Si no se encuentra el tag, se lanza una excepción
    if not row:
        raise HTTPException(status_code=404, detail="No hay tags en uso")

    # Se retorna el tag mas popular
    return row
