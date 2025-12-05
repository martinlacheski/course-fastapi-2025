
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt
from app.core.config import settings


pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: str) -> str:
    expire = datetime.now(
        timezone.utc) + timedelta(settings.JWT_EXPIRES_MINUTES)
    return jwt.encode({"data": data, "expire": expire}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
