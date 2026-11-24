
from pydantic import BaseModel, ConfigDict, Field


class SubcategoryCreate(BaseModel):
    category_id: int = Field(gt=0)
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class SubcategoryUpdate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)


class SubcategoryStatusUpdate(BaseModel):
    is_active: bool


class SubcategoryResponse(BaseModel):
    id: int
    category_id: int
    code: str
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
