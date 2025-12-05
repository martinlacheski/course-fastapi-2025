
from sqlmodel import Session, select
from app.api.user.model import User


# Repositorio de usuarios
class UserRepository:

    # Inicialización de la sesión de la base de datos
    def __init__(self, db: Session):
        self.db = db

    # Obtiene un usuario por su ID
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    # Obtiene un usuario por su correo electrónico
    def get_by_email(self, email: str) -> User | None:
        return self.db.exec(select(User).where(User.email == email)).first()

    # Obtiene un usuario por su nombre de usuario
    def get_by_username(self, username: str) -> User | None:
        return self.db.exec(select(User).where(User.username == username)).first()

    # Crea un nuevo usuario
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
