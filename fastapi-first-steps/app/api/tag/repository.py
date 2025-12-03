from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.tag.models import TagORM


class TagRepository:

    # Constructor
    def __init__(self, db: Session):
        self.db = db

    # Metodo para obtener una etiqueta por su ID

    def get_by_id(self, id: int) -> Optional[TagORM]:
        return self.db.query(TagORM).filter(TagORM.id == id).first()

    # Metodo para obtener una etiqueta por su nombre

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
