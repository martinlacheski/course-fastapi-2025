
from fastapi import APIRouter, status

from app.core.dependencies import DBSession
from app.api.user.model import UserCreate, UserRead
from app.api.user.repository import UserRepository
from app.api.auth.service import AuthService


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DBSession):
    service = AuthService(UserRepository(db))
    return service.register(payload)
