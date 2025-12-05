from pydantic import BaseModel, ConfigDict, Field


# Se crea el modelo de Pydantic para los tags
class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre del tag (mínimo 2 caracteres, máximo 30)")

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)


# Se crea el modelo de Pydantic para crear tags
class TagCreate(TagBase):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la etiqueta")


# Se crea el modelo de Pydantic para actualizar tags
class TagUpdate(TagBase):
    name: str | None = Field(default=None, min_length=2, max_length=30,
                             description="Nombre de la etiqueta")


# Se crea el modelo de Pydantic para devolver la información de las categorias
class TagPublic(TagBase):
    id: int

    model_config = {"from_attributes": True}
