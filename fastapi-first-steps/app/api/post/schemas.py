
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from app.api.tag.schemas import TagCreate
from app.api.category.schemas import CategoryPublic
from app.api.user.schemas import User


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[TagCreate]] = []
    user: Optional[User] = None
    category: Optional[CategoryPublic] = None

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres, máximo 100)",
        examples=["Mi primer post con FastAPI"]
    )
    content: str = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres)",
        examples=["Contenido del post"]
    )

    # Se agrega el ID de la categoria
    category_id: Optional[int] = None
    # Se agrega una lista de tags con un minimo de 1 y un maximo de 5
    tags: List[TagCreate] = Field(..., min_length=1, max_length=5,
                                  description="Tags del post (mínimo 1, máximo 5)"
                                  )


class PostUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres, máximo 100)",
        examples=["Mi primer post con FastAPI"]
    )
    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres)",
        examples=["Contenido del post"]
    )


# Se crea la clase PostPublic para manejar los posts publicados
class PostPublic(PostBase):
    id: int  # Se agrega el ID para que sea único

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


# Se crea la clase PostSummary para manejar los posts resumidos
class PostSummary(BaseModel):
    id: int
    title: str
