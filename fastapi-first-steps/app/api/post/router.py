from fastapi import APIRouter, Query, Depends, HTTPException, Path, status
from typing import Union, Literal, List, Optional
from sqlalchemy.orm import Session
from math import ceil
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.db import get_db
from app.core.security import get_current_user
from .schemas import (PostPublic, PaginatedPost,
                      PostCreate, PostUpdate, PostSummary)
from .repository import PostRepository


# Se crea el router para los endpoints de posts y se le asigna un prefijo y un tag para la documentación
router = APIRouter(prefix="/posts", tags=["Posts"])

########### Endpoints ###########


# Endpoint para obtener posts con búsqueda opcional (Devuelve una lista del modelo PostPublic)
@router.get("/",
            response_model=PaginatedPost
            )
# Búsqueda por titulo
async def get_posts(
    query: Optional[str] = Query(
        default=None,
        description="Buscar en los títulos de los posts",
        alias="search",  # Alias para que el nombre del parámetro sea "search" en la documentación
        min_length=3,  # Minimo 3 caracteres
        max_length=50,  # Maximo 50 caracteres
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"  # Solo letras, numeros y espacios
    ),

    #### Paginación ####

    # Cantidad de resultados por página
    per_page: int = Query(
        10, ge=1, le=50,
        description="Cantidad de resultados por página (1-50)"
    ),

    # Número de página
    page: int = Query(
        1, ge=1,
        description="Número de página (>=1)"
    ),

    # Ordenación
    order_by: Literal["id", "title"] = Query(
        "id", description="Ordenar por id o title"
    ),

    # Dirección de orden
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden (asc o desc)"
    ),

    # se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):

    # Se crea el repositorio
    repository = PostRepository(db)

    # Obtenemos los posts paginados
    query = query if query else None

    # Obtenemos los posts paginados
    total, items = await repository.search(
        query, order_by, direction, page, per_page)

    # Obtenemos el total de paginas
    total_pages = ceil(total/per_page) if total > 0 else 0

    # Obtenemos la pagina actual
    current_page = 1 if total_pages == 0 else min(page, total_pages)

    # Obtenemos si hay anterior y siguiente
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    # Retornamos la lista de posts paginada
    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )


# Endpoint para obtener posts filtrados por etiquetas
@router.get("/by-tags",
            response_model=List[PostPublic]
            )
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    ),
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    # Se crea el repositorio
    repository = PostRepository(db)

    # Obtenemos los posts filtrados por las etiquetas
    return repository.by_tags(tags)


# Endpoint para obtener un post por su ID
@router.get("/{post_id}",
            response_model=Union[PostPublic, PostSummary],
            response_description="Post encontrado"
            )
# Path parameter para controlar el valor del ID del Post
async def get_post(post_id: int = Path(
        ...,
        ge=1,
        title="ID del post",
        description="Identificador del post. Debe ser mayor o igual a 1",
        example=1),
    # Query parameter
    include_content: bool = Query(
        default=True, description="Incluir contenido del post"),
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):

    # Se crea el repositorio
    repository = PostRepository(db)

    # Obtenemos el post
    post = repository.get_by_id(post_id)

    # Si no se encuentra el post, se lanza una excepción
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    # Si se incluye el contenido, se retorna el post completo
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    # Si no se incluye el contenido, se retorna el post resumido
    return PostSummary.model_validate(post, from_attributes=True)


# Endpoint para crear un nuevo post
@router.post("/",
             response_model=PostPublic,
             response_description="Post creado exitosamente",
             status_code=status.HTTP_201_CREATED
             )
# Se recibe el post como un objeto de la clase PostBase
async def create_post(post: PostCreate,
                      # Se inyecta la sesión de la base de datos
                      db: Session = Depends(get_db),
                      # Se valida que el usuario este autenticado
                      user=Depends(get_current_user)):

    # Se crea el repositorio
    repository = PostRepository(db)

    # Se intenta agregar el autor a la base de datos
    try:

        created_post = repository.create(
            title=post.title,
            content=post.content,
            user=post.user.model_dump(),
            tags=[tag.model_dump() for tag in post.tags],
        )

        # Se guardan los cambios en la base de datos
        db.commit()

        # Se refresca el post
        db.refresh(created_post)

        # Se retorna el post
        return created_post

    # Si ocurre un error, se lanza una excepción
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Endpoint para actualizar un post existente
@router.put("/{post_id}",
            response_model=PostPublic,
            response_description="Post actualizado exitosamente"
            )
# Body parameter (datos del POST a actualizar)
async def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):

    # Se crea el repositorio
    repository = PostRepository(db)

    # Obtenemos el post
    post = repository.get_by_id(post_id)

    # Si no se encuentra el post, se lanza una excepción
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    # Se intenta actualizar el post
    try:
        updates = data.model_dump(exclude_unset=True)
        post = repository.update(post, updates)

        # Se guardan los cambios en la base de datos
        db.commit()

        # Se refresca el post
        db.refresh(post)

        # Se retorna el post
        return post

    # Si ocurre un error, se lanza una excepción
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el post")


# Endpoint para eliminar un post por su ID. código de estado 204 (No Content) para la respuesta
@router.delete("/{post_id}",
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_post(post_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    # Se crea el repositorio
    repository = PostRepository(db)

    # Obtenemos el post
    post = repository.get_by_id(post_id)

    # Si no se encuentra el post, se lanza una excepción
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    # Se intenta eliminar el post
    try:
        repository.delete(post)

        # Se guardan los cambios en la base de datos
        db.commit()

    # Si ocurre un error, se lanza una excepción
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el post")
