
from pydantic import BaseModel, ConfigDict, Field


class SubcollectionCreate(BaseModel):
    collection_id: int = Field(gt=0)
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class SubcollectionUpdate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)


class SubcollectionStatusUpdate(BaseModel):
    is_active: bool


class SubcollectionResponse(BaseModel):
    id: int
    collection_id: int
    code: str
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
