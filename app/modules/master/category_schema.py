
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)


class CategoryStatusUpdate(BaseModel):
    is_active: bool


class CategoryResponse(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
