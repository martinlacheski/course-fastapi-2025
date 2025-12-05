

from datetime import datetime
from sqlmodel import Field, SQLModel


# Modelo de usuario
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    surname: str = Field(default="")
    name: str = Field(default="")
    username: str = Field(index=True, unique=True)
    password: str
    created_at: datetime = Field(default=datetime.now())
    is_active: bool = Field(default=True)


##### DTOs #####

# Modelo de usuario para crear
class UserCreate(SQLModel):
    email: str
    surname: str = ""
    name: str = ""
    username: str
    password: str


# Modelo de usuario para leer
class UserRead(SQLModel):
    id: int
    email: str
    surname: str
    name: str
    username: str
    created_at: datetime
    is_active: bool
    model_config = {"from_attributes": True}
