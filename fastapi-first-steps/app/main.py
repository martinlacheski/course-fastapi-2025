
from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv

# Routers
from app.api.post.router import router as post_router
from app.api.auth.router import router as auth_router
from app.api.tag.router import router as tag_router

# Se cargan las variables de entorno
load_dotenv()


# Metodo para crear la aplicacion
def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")

    # Se crean las tablas en la base de datos si no existen (solo en desarrollo)
    Base.metadata.create_all(bind=engine)

    # Se agregan los routers
    app.include_router(auth_router)
    app.include_router(post_router)
    app.include_router(tag_router)

    # Endpoint para la pagina de inicio
    @app.get("/")
    def home():
        return {"message": "Hola Mundo!"}

    # Se retorna la aplicacion
    return app


# Se crea la aplicacion
app = create_app()
