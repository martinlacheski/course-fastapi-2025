
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import DBSession
from app.api.user.repository import UserRepository
from app.api.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(email: str, password: str, db: DBSession):
    service = AuthService(UserRepository(db))
    token = service.login(email, password)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token")
def login(db: DBSession, form: OAuth2PasswordRequestForm = Depends()):
    email = form.username
    password = form.password
    service = AuthService(UserRepository(db))
    token = service.login(email, password)
    return {"access_token": token, "token_type": "bearer"}
