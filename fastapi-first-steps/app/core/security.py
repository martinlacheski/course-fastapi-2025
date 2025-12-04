
from app.api.user.repository import UserRepository
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from pwdlib import PasswordHash
from app.core.config import settings
from app.core.db import get_db
from app.api.user.models import UserORM

password_hash = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"}
)


def create_access_token(subject: str) -> str:
    expire = datetime.now(
        timezone.utc) + timedelta(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"subject": subject, "expire": expire}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY,
                         algorithms=[settings.JWT_ALGORITHM])
    return payload


def raise_invalid_credentials():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Credenciales inválidas")


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"}
    )


def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para acceder a este recurso",
    )


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2)) -> UserORM:

    try:
        payload = decode_token(token)
        subject: Optional[str] = payload.get("subject")
        if not subject:
            raise credentials_exception

        user_id = int(subject)
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exception
    except PyJWTError:
        raise raise_invalid_credentials()

    user = db.get(UserORM, user_id)

    if not user or not user.is_active:
        raise raise_invalid_credentials()

    return user


async def auth2_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise raise_invalid_credentials()
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user: UserORM = Depends(get_current_user)) -> UserORM:
        if order[user["role"]] < order[min_role]:
            raise raise_forbidden()
        return user

    return evaluation


require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")
