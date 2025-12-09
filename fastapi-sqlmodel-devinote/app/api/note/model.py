
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


# Modelo de nota
class Note(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str = ""
    color: Optional[str] = None
    created_at: datetime = Field(default=datetime.now())
    # Relación con el usuario
    owner_id: int = Field(foreign_key="user.id", index=True)


##### DTOs #####


# Modelo de nota para leer
class NoteRead(SQLModel):
    id: int
    title: str
    content: str
    color: Optional[str]
    # Relación con las etiquetas
    label_ids: Optional[list[int]] = None
    # Relación con el usuario
    owner_id: int
    model_config = {"from_attributes": True}


# Modelo de nota para crear
class NoteCreate(SQLModel):
    title: str
    content: str = ""
    color: Optional[str] = None
    # Relación con las etiquetas
    label_ids: Optional[list[int]] = None


# Modelo de nota para actualizar
class NoteUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    color: Optional[str] = None
    # Relación con las etiquetas
    label_ids: Optional[list[int]] = None


# Modelo de nota para leer
class NoteRead(SQLModel):
    id: int
    title: str
    content: str
    color: Optional[str]
    # Relación con las etiquetas
    label_ids: Optional[list[int]] = None
    # Relación con el usuario
    owner_id: int
    model_config = {"from_attributes": True}
