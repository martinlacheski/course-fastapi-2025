
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt
from app.core.config import settings
from fastapi import HTTPException, status


pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def create_access_token(data: dict) -> str:
    expire = datetime.now(
        timezone.utc) + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    expire = expire.isoformat()
    return jwt.encode({"data": data, "expire": expire}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
