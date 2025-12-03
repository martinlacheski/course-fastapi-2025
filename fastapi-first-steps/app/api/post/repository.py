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

    async def search(
            self,
            query: Optional[str],
            order_by: str,
            direction: str,
            page: int,
            per_page: int
    ) -> Tuple[int, List[PostORM]]:

        # Se retorna la lista de posts
        results = self.db.query(PostORM).all()

        # Se retorna la lista de posts filtrada por la búsqueda
        if query:
            results = self.db.execute(select(PostORM).where(
                PostORM.title.contains(query)
            ))

        # Obtenemos el total de resultados
        total = self.db.query(PostORM).count() or 0

        # Si no hay resultados retornamos una lista vacía
        if total == 0:
            return 0, []

        # Obtenemos la página actual
        current_page = min(page, max(1, ceil(total/per_page)))

        # Ordenamos los resultados y aplicamos REVERSE si aplica
        results = self.db.query(PostORM).order_by(
            getattr(PostORM, order_by).desc() if direction == "desc" else getattr(
                PostORM, order_by).asc()
        )

        # Obtenemos los resultados de la página actual
        start = (current_page - 1) * per_page
        # items: List[PostORM] = self.db.execute(results.limit(per_page).offset(start)).scalars().all()
        items: List[PostORM] = results.offset(start).limit(per_page).all()

        return total, items

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
