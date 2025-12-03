from pydantic import BaseModel, ConfigDict, EmailStr


# Se crea el modelo de Pydantic para los autores
class User(BaseModel):
    surname: str
    name: str
    email: EmailStr  # EmailStr comprueba que sea un email valido
    username: str

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)
