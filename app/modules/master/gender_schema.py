
from pydantic import BaseModel, ConfigDict, Field


class GenderCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class GenderUpdate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)


class GenderStatusUpdate(BaseModel):
    is_active: bool


class GenderResponse(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
