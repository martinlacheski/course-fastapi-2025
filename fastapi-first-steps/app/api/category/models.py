
from __future__ import annotations
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.core.db import Base

# Se importa el tipo de datos para que no haya errores de tipado
if TYPE_CHECKING:
    from app.api.post.models import PostORM


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(60), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(
        String(60), unique=True, index=True, nullable=False)

    # Se crea la relacion con el post
    posts: Mapped[List["PostORM"]] = relationship(
        back_populates="category",  # relacion con el post
        lazy="selectin",  # lazy loading
        passive_deletes=True  # para que no se borren los posts al borrar una categoria
    )
