from math import ceil
import os

from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Path, status, Depends
from typing import Union, Literal, List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from sqlalchemy import create_engine, Integer, String, Text, DateTime, select, func, UniqueConstraint, ForeignKey, Table, Column
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column, relationship, selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

if DATABASE_URL:
    print("Conectado a PostgreSQL")
else:
    print("Conectado a SQLite")


# Se crea el engine de la base de datos
engine_kwargs = {}


# Si la base de datos es sqlite, se agrega el parametro check_same_thread
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}


# se asocia el engine con la base de datos
engine = create_engine(DATABASE_URL, **engine_kwargs)


# Se configuracion de la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Se crea la clase base para la base de datos
class Base(DeclarativeBase):
    pass


# Se crea la tabla INTERMEDIA de la relacion muchos a muchos
post_tags = Table(
    "post_tags",  # nombre de la tabla
    Base.metadata,  # metadata de la base de datos
    Column("post_id", ForeignKey("posts.id",
           ondelete="CASCADE"), primary_key=True),  # clave foranea de la tabla posts
    Column("tag_id", ForeignKey("tags.id",
           ondelete="CASCADE"), primary_key=True),  # clave foranea de la tabla tags
)


# Se crea la clase AuthorORM para manejar los autores en la base de datos
class AuthorORM(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now())
    # Se crea la relacion con el post (lado Uno)
    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")


# Se crea la clase TagORM para manejar los tags en la base de datos
class TagORM(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now())

    # Se crea la relacion con el post (lado Uno)
    posts: Mapped[List["PostORM"]] = relationship(
        secondary=post_tags,  # tabla intermedia
        back_populates="tags",  # relacion con el post
        lazy="selectin",  # lazy loading
    )


# Se crea la clase PostORM para manejar los posts en la base de datos
class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now())

    # Se crea la relacion con el post (lado Muchos)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional["AuthorORM"]] = relationship(
        back_populates="posts")

    # Se crea la relacion con el post
    tags: Mapped[List["TagORM"]] = relationship(
        secondary=post_tags,  # tabla intermedia
        back_populates="posts",  # relacion con el post
        lazy="selectin",  # lazy loading
        passive_deletes=True  # para que no se borren los tags al borrar un post
    )


# Entorno de Desarrollo (Producción se ocupan migraciones)
Base.metadata.create_all(bind=engine)


# Conexión con la base de datos
def get_db():
    db = SessionLocal()  # Se crea la sesión de la base de datos
    try:
        yield db  # Se retorna la sesión de la base de datos
    finally:
        db.close()  # Se cierra la sesión de la base de datos


# Se crea la instancia de la aplicacion
app = FastAPI(title="Mini Blog")


################ Se crean las clases para manejar los POSTS ################


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre del tag (mínimo 2 caracteres, máximo 30)")

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str
    email: EmailStr  # EmailStr comprueba que sea un email valido

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = []
    author: Optional[Author] = None

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


################# Endpoints #################

# Endpoint inicial
@app.get("/")
async def home():
    return {"message": "Bienvendidos a Mini Blog"}


# Endpoint para obtener posts con búsqueda opcional (Devuelve una lista del modelo PostPublic)
@app.get("/posts", response_model=PaginatedPost)
async def get_posts(
    # Ejemplo de como advertir que un parámetro esta obsoleto
    text: Optional[str] = Query(
        default=None,
        deprecated=True,    # Indica que el parámetro esta obsoleto
        description="Parámetro obsoleto, usa 'query o search' en su lugar."
    ),
    # Búsqueda por titulo
    query: Optional[str] = Query(
        default=None,
        description="Buscar en los títulos de los posts",
        alias="search",  # Alias para que el nombre del parámetro sea "search" en la documentación
        min_length=3,  # Minimo 3 caracteres
        max_length=50,  # Maximo 50 caracteres
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"  # Solo letras, numeros y espacios
    ),

    ################# Paginación #################

    # Cantidad de resultados por página
    per_page: int = Query(
        10, ge=1, le=50,
        description="Cantidad de resultados por página (1-50)"
    ),

    # Número de página
    page: int = Query(
        1, ge=1,
        description="Número de página (>=1)"
    ),

    # Ordenación
    order_by: Literal["id", "title"] = Query(
        "id", description="Ordenar por id o title"
    ),

    # Dirección de orden
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden (asc o desc)"
    ),

    # se inyecta la sesión de la base de datos
    db: Session = Depends(get_db)
):

    # Se retorna la lista de posts
    results = db.query(PostORM).all()

    # Se asigna a una variable la Query o el texto de búsqueda
    # query = query or text

    # Se retorna la lista de posts filtrada por la búsqueda
    if query:
        results = db.execute(select(PostORM).where(
            PostORM.title.contains(query)
        ))

    # Obtenemos el total de resultados
    total = db.query(PostORM).count()

    # Obtenemos el total de páginas
    total_pages = ceil(total/per_page) if total > 0 else 0

    # Obtenemos la página actual
    if total_pages == 0:
        current_page = 1
    else:
        current_page = min(page, total_pages)

    # Ordenamos los resultados
    # con una funcion anonima ordenamos los resultados y aplicamos REVERSE si aplica
    results = db.query(PostORM).order_by(
        getattr(PostORM, order_by).desc() if direction == "desc" else getattr(
            PostORM, order_by).asc()
    )

    # Obtenemos los resultados de la página actual
    if total_pages == 0:
        items: List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(results.limit(per_page).offset(
            start)).scalars().all()  # [10:20]

    # Obtenemos si hay anterior y siguiente
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    # Retornamos la lista de posts paginada
    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )


@app.get("/posts/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    ),
    db: Session = Depends(get_db)
):
    # Se normalizan los nombres de las etiquetas
    normalized_tag_names = [tag.strip().lower() for tag in tags if tag.strip()]

    # Se retorna una lista vacía si no hay etiquetas
    if not normalized_tag_names:
        return []

    # Se crea la query para obtener los posts filtrados por las etiquetas
    post_list = (
        select(PostORM)
        .options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author),
        ).where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names)))
        .order_by(PostORM.id.asc())
    )

    # Se ejecuta la query y se obtienen los posts
    posts = db.execute(post_list).scalars().all()

    # Se retorna la lista de posts
    return posts


# Endpoint para obtener un post por su ID
@app.get("/posts/{post_id}", response_model=Union[PostPublic, PostSummary], response_description={"Post encontrado"})
async def get_post(post_id: int = Path(
    # Path parameter para controlar el valor del ID del Post
    ...,
    ge=1,
    title="ID del post",
    description="Identificador entero del post. Debe ser mayor a 1",
    example=1
    # Query parameter
), include_content: bool = Query(default=True, description="Incluir contenido del post"), db: Session = Depends(get_db)):

    # Buscamos el post en la base de datos
    post = db.query(PostORM).filter(PostORM.id == post_id).first()

    # Se envia una excepción HTTP si no se encuentra el post
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    # Si tiene contenido, retorna el post completo
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)
    # Si no tiene contenido, retorna el post resumido
    else:
        return PostSummary.model_validate(post, from_attributes=True)


# Endpoint para crear un nuevo post
@app.post("/posts", response_model=PostPublic, response_description={"Post creado exitosamente"}, status_code=status.HTTP_201_CREATED)
# Se recibe el post como un objeto de la clase PostBase
async def create_post(post: PostCreate, db: Session = Depends(get_db)):

    # Se inicializa el autor
    author_obj = None

    # Si el post tiene autor
    if post.author:
        author_obj = db.execute(
            select(AuthorORM).where(
                AuthorORM.email == post.author.email
            )
        ).scalar_one_or_none()

        # Si no se encuentra el autor, se crea
        if not author_obj:
            author_obj = AuthorORM(
                name=post.author.name,
                email=post.author.email
            )
            # Se intenta agregar el autor a la base de datos
            try:
                db.add(author_obj)
                db.commit()
                # db.flush()  # Se fuerza el guardado de la transacción y se obtiene el ID
                # SAWarning: Object of type <PostORM> not in session, add operation along 'AuthorORM.posts' will not proceed
            except IntegrityError as e:
                db.rollback()
                raise HTTPException(status_code=409, detail=str(e))
            except SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

    # Se crea el post
    new_post = PostORM(
        title=post.title,  # Titulo del post
        content=post.content,  # Contenido del post
        author=author_obj  # Autor del post
    )

    # Se visualizan los TAGs del post
    for tag in post.tags:
        tag_obj = db.execute(
            select(TagORM).where(
                TagORM.name.ilike(tag.name)
            )
        ).scalar_one_or_none()

        # Si no se encuentra el tag, se crea
        if not tag_obj:
            tag_obj = TagORM(name=tag.name)
            try:
                db.add(tag_obj)
                db.commit()
                # db.flush()  # Se fuerza el guardado de la transacción y se obtiene el ID
                # SAWarning: Object of type <PostORM> not in session, add operation along 'TagORM.posts' won't proceed
            except IntegrityError as e:
                db.rollback()
                raise HTTPException(status_code=409, detail=str(e))
            except SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

        # Se agrega el tag al post
        new_post.tags.append(tag_obj)

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para actualizar un post existente
@app.put("/posts/{post_id}", response_model=PostPublic, response_description={"Post actualizado exitosamente"})
# Body parameter (datos del POST a actualizar)
async def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):

    # Obtenemos el post
    post = db.query(PostORM).filter(PostORM.id == post_id).first()

    # Se envia una excepción HTTP si no se encuentra el post
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    # Actualizamos el post
    payload = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(post, key, value)

    # Almacenamos los cambios en la base de datos
    try:
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para eliminar un post por su ID
# Path Parameter y código de estado 204 (No Content) para la respuesta
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    # Obtenemos el post
    post = db.query(PostORM).filter(PostORM.id == post_id).first()

    # Si no se encuentra el post
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    # Eliminamos el post
    try:
        db.delete(post)
        db.commit()
        return
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
