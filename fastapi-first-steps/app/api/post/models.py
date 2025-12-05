
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, Table, Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Se importa el tipo de datos para que no haya errores de tipado
if TYPE_CHECKING:
    from app.api.user.models import UserORM
    from app.api.tag.models import TagORM
    from app.api.category.models import CategoryORM


# Se crea la tabla INTERMEDIA de la relacion muchos a muchos
post_tags = Table(
    "post_tags",  # nombre de la tabla
    Base.metadata,  # metadata de la base de datos
    Column("post_id", ForeignKey("posts.id",
           ondelete="CASCADE"), primary_key=True),  # clave foranea de la tabla posts
    Column("tag_id", ForeignKey("tags.id",
           ondelete="CASCADE"), primary_key=True),  # clave foranea de la tabla tags
)


# Se crea la clase PostORM para manejar los posts en la base de datos
class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now())

    # Se crea la relacion con el post (lado Muchos)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Optional["UserORM"]] = relationship(
        back_populates="posts")

    # Se crea la relacion con la categoria
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    category: Mapped[Optional["CategoryORM"]] = relationship(
        back_populates="posts")

    # Se crea la relacion con el post
    tags: Mapped[List["TagORM"]] = relationship(
        secondary=post_tags,  # tabla intermedia
        back_populates="posts",  # relacion con el post
        lazy="selectin",  # lazy loading
        passive_deletes=True  # para que no se borren los tags al borrar un post
    )
