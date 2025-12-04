
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import TokenResponse
from app.api.user.schemas import UserLogin, User
from app.core.security import create_access_token, verify_password
from app.core.db import get_db
from app.api.user.repository import UserRepository
from sqlalchemy.orm import Session


# Se crea el router para la autenticación
router = APIRouter(prefix="/auth", tags=["Auth"])

########### Endpoints ###########


# Endpoint para iniciar sesión
@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Session = Depends(get_db)):

    # Se crea el repositorio
    repository = UserRepository(db)

    # Se busca el usuario por su nombre de usuario
    user = repository.get_by_username(payload.username)

    user_login = {
        "id": user.id,
        "username": user.username,
    }

    # Se verifica que el usuario exista y que la contraseña sea correcta
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Se crea el token
    token = create_access_token(user=user_login)
    return TokenResponse(access_token=token, user=User.model_validate(user))
