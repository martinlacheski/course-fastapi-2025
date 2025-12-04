

from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import TokenResponse, UserPublic
from app.api.user.schemas import UserLogin
from app.core.security import create_access_token, get_current_user, verify_password
from app.core.db import get_db
from app.api.user.repository import UserRepository
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(payload.username)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
async def read_me(current=Depends(get_current_user)):
    return {"email": current["email"], "username": current["username"]}
