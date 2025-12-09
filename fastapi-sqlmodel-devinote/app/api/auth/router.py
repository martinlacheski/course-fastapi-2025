
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import DBSession
from app.api.auth.repository import UserRepository
from app.api.auth.service import AuthService
from app.api.auth.model import UserCreate, UserRead


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DBSession):
    service = AuthService(UserRepository(db))
    return service.register(payload)


@router.post("/login")
def login(username: str, password: str, db: DBSession):
    try:
        service = AuthService(UserRepository(db))
        token = service.login(username, password)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")


@router.post("/token")
def login(db: DBSession, form: OAuth2PasswordRequestForm = Depends()):
    try:
        username = form.username
        password = form.password
        service = AuthService(UserRepository(db))
        token = service.login(username, password)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
