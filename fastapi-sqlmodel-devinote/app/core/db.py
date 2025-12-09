
from typing import Iterator
from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings


# Se crea el engine de la base de datos
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args={
    "check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})


def init_db() -> None:
    if settings.ENVIRONMENT == "DEV":
        """Se inicializa la base de datos con SQLModel y se crean las tablas"""
        SQLModel.metadata.create_all(engine)  # Instancia de Desarrollo
    elif settings.ENVIRONMENT == "PROD":
        """Se inicializa la base de datos con SQLModel y se generan las migraciones con Alembic"""
        pass


def get_session() -> Iterator[Session]:
    """Devuelve una sesión de la base de datos gestionada como un contexto"""
    with Session(engine) as session:
        yield session
