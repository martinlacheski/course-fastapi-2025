
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.user.models import UserORM


class UserRepository:

    ########### Constructor ###########
    def __init__(self, db: Session):
        self.db = db

    ########### Metodo para obtener un usuario por su id ###########

    def get(self, user_id: int) -> UserORM | None:
        return self.db.get(UserORM, user_id)

    ########### Metodo para obtener un usuario por su email ###########

    def get_by_email(self, email: str) -> UserORM | None:
        query = select(UserORM).where(UserORM.email == email)
        return self.db.execute(query).scalar_one_or_none()

    ########### Metodo para obtener un usuario por su username ###########

    def get_by_username(self, username: str) -> UserORM | None:
        query = select(UserORM).where(UserORM.username == username)
        return self.db.execute(query).scalar_one_or_none()

    ########### Metodo para crear un usuario ###########

    def create(self, email: str, password: str, name: str, surname: str, username: str) -> UserORM:
        db_user = UserORM(
            email=email,
            password=password,
            name=name,
            surname=surname,
            username=username
        )

        # Guardamos el Objeto Usuario
        self.db.add(db_user)
        self.db.flush()
        self.db.refresh(db_user)
        return db_user

    ########### Metodo para actualizar un usuario ###########

    def update(self, user: UserORM, update_data: dict) -> UserORM:
        for key, value in update_data.items():
            setattr(user, key, value)

        return user

    ########### Metodo para eliminar un usuario ###########

    def delete(self, user: UserORM) -> None:
        self.db.delete(user)
