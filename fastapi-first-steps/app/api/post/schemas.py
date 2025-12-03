
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Literal
from app.api.tag.schemas import Tag
from app.api.user.schemas import User


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = []
    user: Optional[User]

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

    # Se agrega una lista de tags con un minimo de 1 y un maximo de 5
    tags: List[Tag] = Field(..., min_length=1, max_length=5,
                            description="Tags del post (mínimo 1, máximo 5)"
                            )

    user: User = Field(..., description="Usuario del post")


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


# Se crea la clase PaginatedPost para manejar los posts paginados
class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]
