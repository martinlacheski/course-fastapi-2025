from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Se importa el tipo de datos para que no haya errores de tipado
if TYPE_CHECKING:
    from app.api.post.models import PostORM


# Se crea la clase UserORM para manejar los usuarios en la base de datos
class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    surname: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now())
    # Se crea la relacion con el post (lado Uno)
    posts: Mapped[List["PostORM"]] = relationship(back_populates="user")
