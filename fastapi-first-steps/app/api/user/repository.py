from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.user.models import UserORM


class UserRepository:

    # Constructor
    def __init__(self, db: Session):
        self.db = db

    # Metodo para obtener un usuario por su email

    def get_by_email(self, email: str) -> UserORM | None:
        return self.db.query(UserORM).filter(UserORM.email == email).first()

    # Metodo para obtener un usuario por su email

    def ensure_user(self, surname: str, name: str, email: str) -> UserORM:

        user_obj = self.db.execute(
            select(UserORM).where(UserORM.email == email)
        ).scalar_one_or_none()

        if user_obj:
            return user_obj

        user_obj = UserORM(surname=surname,
                           name=name,
                           email=email)
        self.db.add(user_obj)
        self.db.flush()

        return user_obj
