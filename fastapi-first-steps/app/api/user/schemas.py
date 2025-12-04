from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


# Se crea el modelo de Pydantic para los autores

class User(BaseModel):
    id: int | None = None
    surname: str = Field(min_length=3, max_length=50,
                         description="Apellido del usuario")
    name: str = Field(min_length=3, max_length=50,
                      description="Nombre del usuario")
    email: EmailStr
    username: str = Field(min_length=3, max_length=50,
                          description="Nombre de usuario")
    password: str = Field(min_length=6, max_length=255,
                          description="Contraseña")
    role: str = Field(default="user", description="Rol del usuario")
    is_active: bool | None = Field(default=True, description="Estado")
    created_at: datetime | None = Field(
        default=datetime.now(), description="Fecha de creacion")

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


# Se crea el modelo de Pydantic para la publicacion de usuarios
class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    model_config = ConfigDict(from_attributes=True)


# Se crea el modelo de Pydantic para la autenticacion de usuarios
class UserLogin(BaseModel):
    username: str
    password: str
