
from pydantic import BaseModel, ConfigDict, Field


class MetalCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)


class MetalUpdate(BaseModel):
    code: str | None = Field(
        None, min_length=1, max_length=50
    )
    name: str | None = Field(
        None, min_length=1, max_length=100
    )
    is_active: bool | None = None


class MetalResponse(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
