from app.api.post.schemas import PostPublic
from app.services.pagination import paginate_query
from typing import List, Optional, Tuple
from math import ceil

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload
from app.api.post.models import PostORM
from app.api.user.models import UserORM
from app.api.tag.models import TagORM
from app.api.user.repository import UserRepository
from app.api.tag.repository import TagRepository


class PostRepository:

    ########### Constructor ###########
    def __init__(self, db: Session):
        self.db = db

    ########### Metodo para obtener un post por su ID ###########

    def get_by_id(self, id: int) -> Optional[PostORM]:
        return self.db.query(PostORM).filter_by(id=id).first()

    ########### Metodo para buscar posts ###########

    def search(
            self,
            search: Optional[str],
            order_by: str,
            direction: str,
            page: int,
            per_page: int
    ):

        # Se retorna la lista de posts
        # results = self.db.query(PostORM).all()
        query = select(PostORM)

        # Se retorna la lista de posts filtrada por la búsqueda
        if search:
            query = query.where(PostORM.title.contains(search))

        # Se definen los ordenamientos permitidos en la paginación
        allowed_order = {
            "id": PostORM.id,
            "title": func.lower(PostORM.title),
        }

        # Se ejecuta la query con la paginación
        result = paginate_query(
            db=self.db,
            model=PostORM,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        # Se mapea la query a PostPublic para que la respuesta sea un JSON
        result["items"] = [PostPublic.model_validate(
            item) for item in result["items"]]

        # Se retorna el resultado
        return result

    ########### Metodo para buscar posts por tags ###########

    def by_tags(self, tags: List[str]) -> List[PostORM]:

        # Se normalizan los nombres de las etiquetas
        normalized_tag_names = [tag.strip().lower()
                                for tag in tags if tag.strip()]

        # Si no hay etiquetas, retornamos una lista vacía
        if not normalized_tag_names:
            return []

        # Se crea la query para obtener los posts filtrados por las etiquetas
        post_list = (
            select(PostORM)
            .options(
                selectinload(PostORM.tags),
                joinedload(PostORM.user),
            ).where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names)))
            .order_by(PostORM.id.asc())
        )

        # Se ejecuta la query y se retorna la lista con los posts
        return list(self.db.execute(post_list).scalars().all())

    ########### Metodo para crear un post ###########

    def create(self, title: str, content: str, user: UserORM, tags: List[dict]) -> PostORM:
        # Obtenemos el Usuario
        user_obj = None
        if user:
            # Obtenemos el usuario desde el repositorio de usuarios
            user_obj = UserRepository(
                self.db).get_user(user)

        # Creamos el Objeto Post
        post = PostORM(title=title, content=content, user=user_obj)

        # Asignamos las etiquetas al Objeto Post
        for tag in tags:
            # Obtenemos las etiquetas desde el repositorio de etiquetas
            tag_obj = TagRepository(self.db).get_by_name(tag["name"])
            post.tags.append(tag_obj)

        # Guardamos el Objeto Post
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)

        return post

    ########### Metodo para actualizar un post ###########

    def update(self, post: PostORM, update_data: dict) -> PostORM:
        for key, value in update_data.items():
            setattr(post, key, value)

        return post

    ########### Metodo para eliminar un post ###########

    def delete(self, post: PostORM) -> None:
        self.db.delete(post)
