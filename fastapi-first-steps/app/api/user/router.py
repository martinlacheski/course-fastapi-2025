

from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import UserPublic
from app.api.user.schemas import User
from app.core.db import get_db
from app.api.user.repository import UserRepository
from app.core.security import get_current_user, hash_password
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user", tags=["User"])


########### Endpoints ###########


# Endpoint para registrar un nuevo usuario
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(payload: User, db: Session = Depends(get_db)):

    # Se crea el repositorio
    repository = UserRepository(db)

    # Si el usuario ya existe, se lanza una excepción
    if repository.get_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con el email seleccionado, intente con otro"
        )

    if repository.get_by_username(payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con el nombre de usuario seleccionado, intente con otro"
        )

    # Se crea el usuario
    user = repository.create(
        surname=payload.surname,
        name=payload.name,
        email=payload.email,
        username=payload.username,
        password=hash_password(payload.password)
    )

    # Se guardan los cambios en la base de datos
    db.commit()

    # Se refresca el usuario
    db.refresh(user)

    # Se retorna el usuario
    return User.model_validate(user)


# Endpoint para obtener los datos del usuario actual
@router.get("/me", response_model=UserPublic)
async def read_me(current: User = Depends(get_current_user)):
    return UserPublic.model_validate(current)
