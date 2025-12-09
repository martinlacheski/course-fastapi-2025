
from sqlmodel import Session, select
from app.api.auth.model import User


# Repositorio de usuarios
class UserRepository:

    # Inicialización de la sesión de la base de datos
    def __init__(self, db: Session):
        self.db = db

    # Obtiene un usuario por su ID
    def get_by_id(self, user_id: int) -> User | None:
        try:
            return self.db.get(User, user_id)
        except Exception as e:
            print(f"Error al obtener el usuario por ID: {e}")
            return None

    # Obtiene un usuario por su correo electrónico
    def get_by_email(self, email: str) -> User | None:
        try:
            return self.db.exec(select(User).where(User.email == email)).first()
        except Exception as e:
            print(f"Error al obtener el usuario por correo electrónico: {e}")
            return None

    # Obtiene un usuario por su nombre de usuario
    def get_by_username(self, username: str) -> User | None:
        try:
            return self.db.exec(select(User).where(User.username == username)).first()
        except Exception as e:
            print(f"Error al obtener el usuario por nombre de usuario: {e}")
            return None

    # Crea un nuevo usuario
    def create(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            print(f"Error al crear el usuario: {e}")
            return None
