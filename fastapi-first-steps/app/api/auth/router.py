import os
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import Token, UserPublic
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, get_current_user

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


FAKE_USERS = {
    "martin@fastapi.com": {
        "email": "martin@fastapi.com",
        "surname": "Lacheski",
        "name": "Martin",
        "username": "martin",
        "password": "ninguna"
    }
}

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token(
        data={
            "email": user["email"],
            "username": user["username"],
            "surname": user["surname"],
            "name": user["name"]
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
async def read_me(current=Depends(get_current_user)):
    return {"email": current["email"], "username": current["username"]}
