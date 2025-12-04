
from app.core.config import settings
from pydantic import BaseModel
from app.api.user.schemas import UserPublic


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    minutes_to_expire: int = int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    user: UserPublic
