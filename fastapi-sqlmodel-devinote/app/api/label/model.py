

from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


# Modelo de etiqueta
class Label(SQLModel, table=True):

    # Restricción de unicidad #
    # se asegura de que no haya dos etiquetas con el mismo nombre para el mismo usuario

    __table_args__ = (UniqueConstraint(
        "owner_id", "name", name="uq_label_owner_name"),)

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=50)
    created_at: datetime = Field(default=datetime.now())
    # Relación con el usuario
    owner_id: int = Field(foreign_key="user.id", index=True)


# Modelo de etiqueta de nota (tabla intermedia)
class NoteLabelLink(SQLModel, table=True):

    # Restricción de unicidad #
    # se asegura de que no haya dos etiquetas con el mismo nombre para la misma nota

    __table_args__ = (UniqueConstraint(
        "note_id", "label_id", name="uq_label_owner_name"),)

    id: int = Field(default=None, primary_key=True)
    # Relación con la nota
    note_id: int = Field(foreign_key="note.id", index=True)
    # Relación con la etiqueta
    label_id: int = Field(foreign_key="label.id", index=True)


##### DTOs #####

# Modelo de etiqueta para crear
class LabelCreate(SQLModel):
    name: str


# Modelo de etiqueta para leer
class LabelRead(SQLModel):
    id: int
    name: str
    model_config = {"from_attributes": True}
