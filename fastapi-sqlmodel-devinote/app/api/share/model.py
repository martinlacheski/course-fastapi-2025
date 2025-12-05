
from datetime import datetime
from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


# Roles de compartir: si puede leer, editar o eliminar
class ShareRole(str, Enum):
    READ = "read"
    EDIT = "edit"
    DELETE = "delete"


# Modelo de compartir notas
class NoteShare(SQLModel, table=True):

    # Restricción de unicidad #
    # se asegura de que no haya mas de una vez la misma nota compartida con el mismo usuario

    __table_args__ = (UniqueConstraint(
        "note_id", "user_id", name="uq_note_user"),)

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    # Relación con la nota
    note_id: int = Field(foreign_key="note.id", index=True)
    # Relación con el usuario
    user_id: int = Field(foreign_key="user.id", index=True)
    # Rol de compartir
    role: ShareRole = Field(default=ShareRole.READ)


# Modelo de compartir etiquetas
class LabelShare(SQLModel, table=True):

    # Restricción de unicidad #
    # se asegura de que no haya mas de una vez la misma etiqueta compartida con el mismo usuario

    __table_args__ = (UniqueConstraint(
        "label_id", "user_id", name="uq_label_user"),)

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    # Relación con la etiqueta
    label_id: int = Field(foreign_key="label.id", index=True)
    # Relación con el usuario
    user_id: int = Field(foreign_key="user.id", index=True)
    # Rol de compartir
    role: ShareRole = Field(default=ShareRole.READ)


# Modelo de solicitud de compartir
class ShareRequest(SQLModel):
    target_user_id: int = Field(gt=0)
    role: ShareRole = ShareRole.READ
