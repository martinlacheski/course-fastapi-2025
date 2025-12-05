
from math import ceil
from typing import Any, Optional, Dict
from sqlmodel import Session, select, func


DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


# Sanitiza la paginación
def sanitize_pagination(page: int = 1, per_page: int = DEFAULT_PER_PAGE):
    # Se valida que la página sea mayor o igual a 1
    page = max(1, int(page or 1))
    # Se valida que el número de elementos por página sea mayor o igual a 1 y menor o igual a 100
    per_page = min(MAX_PER_PAGE, max(1, int(per_page or DEFAULT_PER_PAGE)))
    # Se retorna la página y el número de elementos por página
    return page, per_page


# Función para obtener los resultados paginados
def paginate_query(
    db: Session,
    model,
    base_query=None,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
    order_by: Optional[str] = None,
    direction: str = "asc",
    allowed_order: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    page, per_page = sanitize_pagination(page, per_page)
    # Se crea la consulta base
    query = base_query if base_query is not None else select(model)

    # Se obtiene el total de registros
    total = db.scalar(select(func.count()).select_from(model)) or 0

    # Si no hay registros, se retorna un diccionario con la información de la paginación
    if total == 0:
        return {"total": 0, "pages": 0, "page": page, "per_page": per_page, "items": []}

    # Si se especifica y permite el ordenamiento
    if allowed_order and order_by:
        if order_by in allowed_order:
            col = allowed_order[order_by]
        else:
            col = allowed_order.get("id")  # fallback

        if col is not None:
            query = query.order_by(
                col.desc() if direction == "desc" else col.asc())

    # Se obtienen los elementos
    items = db.exec(query.offset(
        (page-1) * per_page).limit(per_page)).all()

    # Se retorna la información de la paginación
    return {
        "total": total,
        "pages": ceil(total/per_page),
        "page": page,
        "per_page": per_page,
        "items": items
    }
