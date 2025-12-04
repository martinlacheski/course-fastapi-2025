from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.user.models import UserORM


class UserRepository:

    # Constructor
    def __init__(self, db: Session):
        self.db = db

    # Metodo para obtener un usuario por su email
    def get_user(self, user: dict) -> Optional[UserORM]:

        user_obj = self.db.execute(
            select(UserORM).where(UserORM.email.ilike(user["email"]))
        ).scalar_one_or_none()

        if user_obj:
            return user_obj

        # Crear UNA sola instancia y asociarla a la sesión
        user_obj = UserORM(**user)
        self.db.add(user_obj)
        self.db.flush()   # para que tenga id si la PK es autoincremental

        return user_obj
