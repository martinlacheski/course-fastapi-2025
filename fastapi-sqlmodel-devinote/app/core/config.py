
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuración del .env en Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRES_MINUTES: int
    PROJECT_NAME: str
    ENVIRONMENT: str


settings = Settings()  # ty:ignore[missing-argument]
