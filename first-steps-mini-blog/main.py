from typing import Union
from pydantic.functional_validators import field_validator
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

app = FastAPI(tittle="Mini Blog")

BLOG_POSTS = [
    {"id": 1, "title": "Primer Post", "content": "Post sobre Python"},
    {"id": 2, "title": "Segundo Post", "content": "Post sobre FastAPI"},
    {"id": 3, "title": "Tercer Post", "content": "Post sobre FastAPI vs Django"},
]

################ Se crean las clases para manejar los POSTS ################


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre del tag (mínimo 2 caracteres, máximo 30)")


class Author(BaseModel):
    name: str
    email: EmailStr  # EmailStr valida que sea un email valido


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = []
    author: Optional[Author] = None


class PostCreate(BaseModel):
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

    # Se agrega una lista de tags con un minimo de 1 y un maximo de 5
    tags: List[Tag] = Field(..., min_items=1, max_items=5,
                            description="Tags del post (mínimo 1, máximo 5)")

    author: Author = Field(..., description="Autor del post")

    # Validador para que el titulo sea único
    @field_validator("title")
    @classmethod  # Indica que es un método de clase
    def title_must_be_unique(cls, value):
        if value in [post["title"] for post in BLOG_POSTS]:
            raise ValueError(
                "El titulo debe ser único, ya existe en los Posts")
        return value


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


class PostSummary(BaseModel):
    id: int
    title: str


################# Endpoints #################

# Endpoint inicial
@app.get("/")
async def home():
    return {"message": "Bienvendidos a Mini Blog"}


# Endpoint para obtener posts con búsqueda opcional (Devuelve una lista del modelo PostPublic)
@app.get("/posts", response_model=List[PostPublic])
async def get_posts(query: str | None = Query(default=None, description="Buscar en los posts")):  # Query parameter

    if query:
        # Se retornan los posts que coinciden con la búsqueda en QUERY
        return [post for post in BLOG_POST if query.lower() in post["title"].lower()]

    # Se retornan todos los posts si no hay QUERY
    return BLOG_POSTS


# Endpoint para obtener un post por su ID con Path Parameter
@app.get("/posts/{post_id}", response_model=Union[PostPublic, PostSummary], response_description={"Post encontrado"})
async def get_post(post_id: int, include_content: bool = Query(default=True, description="Incluir contenido del post")):  # Query parameter

    # Union[PostPublic, PostSummary].
    # Intenta encontrar el post en PostPublic, si no lo encuentra, intenta encontrarlo en PostSummary
    for post in BLOG_POSTS:
        if post["id"] == post_id:
            if include_content:
                return post
            else:
                return {"id": post["id"], "title": post["title"]}

    # Se envia una excepción HTTP si no se encuentra el post
    raise HTTPException(status_code=404, detail="Post no encontrado")


# Endpoint para crear un nuevo post
@app.post("/posts", response_model=PostPublic, response_description={"Post creado exitosamente"})
# Se recibe el post como un objeto de la clase PostBase
async def create_post(post: PostCreate):

    # Se obtiene el numero de ID nuevo desde el maximo ID existente
    new_id = max(post["id"] for post in BLOG_POSTS) + 1 if BLOG_POSTS else 1
    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        # Se convierte el tag en un diccionario
        "tags": [tag.model_dump() for tag in post.tags],
        # Se convierte el author en un diccionario
        "author": post.author.model_dump() if post.author else None
    }

    # Se agrega el nuevo post a la lista
    BLOG_POSTS.append(new_post)

    # Se retorna el nuevo post creado
    return new_post


# Endpoint para actualizar un post existente
# Endpoint con path parameter
@app.put("/posts/{post_id}", response_model=PostPublic, response_description={"Post actualizado exitosamente"})
# Body parameter (datos del POST a actualizar)
async def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POSTS:
        if post["id"] == post_id:
            # Excluye los campos que no se envian
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload:
                post["title"] = payload["title"]
            if "content" in payload:
                post["content"] = payload["content"]
            return post

    # Se envia una excepción HTTP si no se encuentra el post
    raise HTTPException(status_code=404, detail="Post no encontrado")


# Endpoint para eliminar un post por su ID
# Path Parameter y código de estado 204 (No Content) para la respuesta
@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: int):
    # Iteramos con el indice y el post para eliminar, usando enumerate para obtener el índice
    for index, post in enumerate(BLOG_POSTS):
        if post["id"] == post_id:
            # Eliminamos el post usando POP con el índice
            BLOG_POSTS.pop(index)
            # Retornamos una respuesta vacía con el código de estado 204 (No Content)
            return

    # Se envia una excepción HTTP si no se encuentra el post
    raise HTTPException(status_code=404, detail="Post no encontrado")
