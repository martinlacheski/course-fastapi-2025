
from fastapi import HTTPException, status

from app.api.user.model import User, UserCreate
from app.api.user.repository import UserRepository
from app.core.security import (create_access_token, hash_password,
                               verify_password)


# Clase de servicio de autenticación
class AuthService:

    # Inicialización de la clase
    def __init__(self, repo: UserRepository):
        self.repo = repo

    # Registro de un nuevo usuario
    def register(self, payload: UserCreate) -> User:

        # Verificar si el email ya está registrado
        if self.repo.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")

        # Verificar si el username ya está registrado
        if self.repo.get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username ya registrado")

        # Crear el usuario
        user = User(
            email=payload.email,
            surname=payload.surname,
            name=payload.name,
            username=payload.username,
            password=payload.password,
        )

        # Retornar el usuario creado
        return self.repo.create(user)

    # Login de un usuario
    def login(self, username: str, password: str) -> str:

        # Verificar si el usuario existe
        user = self.repo.get_by_username(username)

        # Se genera el payload del usuario
        user_login = {
            "id": user.id,  # type: ignore
            "username": user.username,  # type: ignore
        }

        # Se verifica que el usuario exista y que la contraseña sea correcta
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

        # Generar el token
        token = create_access_token(data=str(user_login))
        return token
