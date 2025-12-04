
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.tag.schemas import TagPublic
from app.api.tag.models import TagORM
from app.services.pagination import paginate_query


class TagRepository:

    ########### Constructor ###########
    def __init__(self, db: Session):
        self.db = db

    ########### Metodo para obtener una tag por su ID ###########

    def get_by_id(self, id: int) -> Optional[TagORM]:
        return self.db.query(TagORM).filter(TagORM.id == id).first()

    ########### Metodo para obtener una tag por su nombre ###########

    def get_by_name(self, name: str) -> TagORM:
        tag_obj = self.db.execute(
            select(TagORM).where(TagORM.name.ilike(name))
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()
        return tag_obj

    ########### Metodo para listar las tags ###########

    def list_tags(
        self,
        search: Optional[str],
        order_by: str = "id",
        direction: str = "asc",
        page: int = 1,
        per_page: int = 10
    ):
        # Se crea la query
        query = select(TagORM)

        # Se verifica si hay busqueda
        if search:
            query = query.where(func.lower(
                TagORM.name).ilike(f"%{search.lower()}%"))

        # Se definen los ordenamientos permitidos
        allowed_order = {
            "id": TagORM.id,
            "name": func.lower(TagORM.name),
        }

        # Se ejecuta la query
        result = paginate_query(
            db=self.db,
            model=TagORM,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        # Se mapea la query
        result["items"] = [TagPublic.model_validate(
            item) for item in result["items"]]

        # Se retorna el resultado
        return result

    ########### Metodo para crear un tag ###########

    def create_tag(self, name: str) -> TagORM:

        # Se normaliza el nombre de la etiqueta
        normalize = name.strip().lower()

        # Se verifica si la etiqueta ya existe
        tag = TagORM(name=normalize)

        # Se agrega la etiqueta a la base de datos
        self.db.add(tag)

        # Se guardan los cambios en la base de datos
        self.db.flush()

        # Se refresca la etiqueta
        self.db.refresh(tag)

        # Se retorna la etiqueta
        return tag

    ########### Metodo para actualizar un tag ###########

    def update(self, tag: TagORM, update_data: dict) -> TagORM:
        for key, value in update_data.items():
            setattr(tag, key, value)

        print(tag)
        return tag

    ########### Metodo para eliminar un tag ###########

    def delete(self, tag: TagORM) -> None:
        self.db.delete(tag)

    ########### Metodo para obtener la tag mas popular ###########

    def most_popular(self) -> dict | None:

        # Se verifica si hay tags
        row = (
            self.db.execute(
                # Se seleccionan los campos
                select(
                    TagORM.id.label("id"),
                    TagORM.name.label("name"),
                    func.count(PostORM.id).label("uses")
                )
                # Se hace la union de las tablas
                .join(post_tags, post_tags.c.tag_id == TagORM.id)
                .join(PostORM, PostORM.id == post_tags.c.post_id)
                .group_by(TagORM.id, TagORM.name)
                # Se ordena por la cantidad de usos
                .order_by(func.count(PostORM.id).desc(), func.lower(TagORM.name).asc())
                # Se limita a 1 para obtener la mas popular
                .limit(1)
            )
            .mappings()
            .first()
        )

        # Si no hay tags, se retorna None
        return dict(row) if row else None
