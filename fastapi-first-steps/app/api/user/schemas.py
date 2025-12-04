from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Se crea el modelo de Pydantic para los autores
class User(BaseModel):
    surname: str
    name: str
    email: EmailStr  # EmailStr comprueba que sea un email valido
    username: str = Field(min_length=3, max_length=50,
                          description="Nombre de usuario")
    password: str = Field(min_length=6, max_length=72)

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


# Se crea el modelo de Pydantic para la creacion de usuarios
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    surname: str = Field(min_length=3, max_length=50,
                         description="Apellido del usuario")
    name: str = Field(min_length=3, max_length=50,
                      description="Nombre del usuario")
    username: str = Field(min_length=3, max_length=50,
                          description="Nombre de usuario")
    password: str = Field(min_length=6, max_length=72,
                          description="Contraseña")


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
