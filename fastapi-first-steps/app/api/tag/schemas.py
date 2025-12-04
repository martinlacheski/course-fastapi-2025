from pydantic import BaseModel, ConfigDict, Field


# Se crea el modelo de Pydantic para los tags
class TagPublic(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre del tag (mínimo 2 caracteres, máximo 30)")

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


# Se crea el modelo de Pydantic para crear tags
class TagCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la etiqueta")


# Se crea el modelo de Pydantic para actualizar tags
class TagUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la etiqueta")


# Se crea el modelo de Pydantic para los tags con la cantidad de usos
class TagWithCount(TagPublic):
    uses: int
