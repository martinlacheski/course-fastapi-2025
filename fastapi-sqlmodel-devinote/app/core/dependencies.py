

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_token
from app.api.auth.model import User
from app.api.auth.repository import UserRepository

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


# Método para obtener la sesión de la base de datos
def get_db() -> Session:
    return next(get_session())


# Se envuelve la dependencia de la sesión en un Annotated para que sea tipado
# db: Session = Depends(get_db)
DBSession = Annotated[Session, Depends(get_db)]
# db: DBSession


# Método para obtener el usuario actual
def get_current_user(token: Annotated[str, Depends(oauth2)], db: DBSession) -> User:

    # Excepción para cuando el token no es válido
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Se intenta decodificar el token
    try:
        payload = decode_token(token)
        data = payload.get("data")

        # Si no hay datos o el id no está en los datos, se lanza la excepción
        if not data or "id" not in data:
            raise credentials_exc

        # Se obtiene el id del usuario
        user_id = int(data["id"])
    except Exception:
        raise credentials_exc

    # Se intenta obtener el usuario
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    # Si el usuario no existe, se lanza la excepción
    if not user:
        raise credentials_exc

    # Se retorna el usuario
    return user


# Se envuelve la dependencia del usuario en un Annotated para que sea tipado
CurrentUser = Annotated[User, Depends(get_current_user)]
