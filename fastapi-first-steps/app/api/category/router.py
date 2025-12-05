
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.category.repository import CategoryRepository
from app.core.db import get_db
from app.core.security import get_current_user
from app.api.category.schemas import CategoryCreate, CategoryUpdate, CategoryPublic

router = APIRouter(prefix="/categories", tags=["Categories"])


########### Endpoints ###########


# Endpoint para obtener categorías con búsqueda opcional (Devuelve una lista del modelo CategoryPublic)
# @router.get("/", response_model=list[CategoryPublic])
# def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
#     repository = CategoryRepository(db)
#     return repository.list_many(skip=skip, limit=limit)


# Endpoint para búsqueda por nombre o slug
@router.get("/",
            response_model=dict
            )
async def list_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order_by: str = Query("id", pattern="^(id|name|slug)$"),
    direction: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    repository = CategoryRepository(db)
    return repository.list_categories(
        page=page,
        per_page=per_page,
        order_by=order_by,
        direction=direction,
        search=search
    )


# Endpoint para crear una categoría
@router.post("/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    repository = CategoryRepository(db)
    exist = repository.get_by_slug(data.slug)
    if exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slug en uso")

    category = repository.create(name=data.name, slug=data.slug)
    db.commit()
    db.refresh(category)
    return category


# Endpoint para obtener una categoría por ID
@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(
    category_id: int,
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    repository = CategoryRepository(db)
    category = repository.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Categoría no encontrada")

    return category


# Endpoint para actualizar una categoría
@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    # Se inyecta la sesión de la base de datos
    db: Session = Depends(get_db),
    # Se valida que el usuario este autenticado
    user=Depends(get_current_user)
):
    repository = CategoryRepository(db)
    category = repository.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Categoría no encontrada")

    updated = repository.update(category, data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(updated)
    return updated


# Endpoint para eliminar una categoría
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    category = repository.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Categoría no encontrada")

    repository.delete(category)
    db.commit()
    return None
