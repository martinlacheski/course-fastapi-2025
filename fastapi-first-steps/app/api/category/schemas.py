from pydantic import BaseModel, ConfigDict, Field


# Se crea el modelo de Pydantic para las categorias
class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    slug: str = Field(min_length=2, max_length=60)

    # Se configura el modelo de Pydantic para que se pueda convertir a JSON
    model_config = ConfigDict(from_attributes=True)

# Se crea el modelo de Pydantic para las categorias a crear


class CategoryCreate(CategoryBase):
    pass


# Se crea el modelo de Pydantic para las categorias a actualizar
class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=60)
    slug: str | None = Field(default=None, min_length=2, max_length=60)


# Se crea el modelo de Pydantic para devolver la información de las categorias
class CategoryPublic(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
