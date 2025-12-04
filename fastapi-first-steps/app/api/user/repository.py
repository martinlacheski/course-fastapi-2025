from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.user.models import UserORM


class UserRepository:

    # Constructor
    def __init__(self, db: Session):
        self.db = db

    # Metodo para obtener un usuario por su id
    def get(self, user_id: int) -> UserORM | None:
        return self.db.get(UserORM, user_id)

    # Metodo para obtener un usuario por su email
    def get_by_email(self, email: str) -> UserORM | None:
        query = select(UserORM).where(UserORM.email == email)
        return self.db.execute(query).scalar_one_or_none()
