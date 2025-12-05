
from typing import Sequence, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.services.pagination import paginate_query
from app.api.category.models import CategoryORM
from app.api.category.schemas import CategoryPublic


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_many(self, *, skip: int = 0, limit: int = 50) -> Sequence[CategoryORM]:
        query = (select(CategoryORM).offset(skip).limit(limit))
        return self.db.execute(query).scalars().all()

    def list_categories(
        self,
        search: Optional[str],
        order_by: str = "id",
        direction: str = "asc",
        page: int = 1,
        per_page: int = 10
    ):
        # Se crea la query
        query = select(CategoryORM)

        # Se verifica si hay busqueda
        if search:
            query = query.where(func.lower(
                CategoryORM.name).ilike(f"%{search.lower()}%"))

        # Se definen los ordenamientos permitidos en la paginación
        allowed_order = {
            "id": CategoryORM.id,
            "name": func.lower(CategoryORM.name),
            "slug": func.lower(CategoryORM.slug)
        }

        # Se ejecuta la query con la paginación
        result = paginate_query(
            db=self.db,
            model=CategoryORM,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        # Se mapea la query a CategoryPublic para que la respuesta sea un JSON
        result["items"] = [CategoryPublic.model_validate(
            item) for item in result["items"]]

        # Se retorna el resultado
        return result

    def list_with_total(self, *, page: int = 1, per_page: int = 50) -> tuple[int, list[CategoryORM]]:
        pass

    def get(self, category_id: int) -> CategoryORM | None:
        return self.db.get(CategoryORM, category_id)

    def get_by_slug(self, slug: str) -> CategoryORM | None:
        query = select(CategoryORM).where(CategoryORM.slug == slug)
        return self.db.execute(query).scalars().first()

    def create(self, *, name: str, slug: str) -> CategoryORM:
        category = CategoryORM(name=name, slug=slug)
        self.db.add(category)
        self.db.flush()
        return category

    def update(self, category: CategoryORM, updates: dict) -> CategoryORM:
        # allowed_items = {"name", "slug"}
        for key, value in updates.items():
            setattr(category, key, value)

        self.db.add(category)
        self.db.flush()
        return category

    def delete(self, category: CategoryORM) -> None:
        self.db.delete(category)
