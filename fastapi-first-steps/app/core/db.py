from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

if DATABASE_URL:
    print("Conectado a PostgreSQL")
else:
    print("Conectado a SQLite")


# Se crea el engine de la base de datos
engine_kwargs = {}


# Si la base de datos es sqlite, se agrega el parametro check_same_thread
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}


# se asocia el engine con la base de datos
engine = create_engine(DATABASE_URL, **engine_kwargs)


# Se configuracion de la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Se crea la clase base para la base de datos
class Base(DeclarativeBase):
    pass


# Entorno de Desarrollo (Producción se ocupan migraciones)
Base.metadata.create_all(bind=engine)


# Conexión con la base de datos
def get_db():
    db = SessionLocal()  # Se crea la sesión de la base de datos
    try:
        yield db  # Se retorna la sesión de la base de datos
    finally:
        db.close()  # Se cierra la sesión de la base de datos
