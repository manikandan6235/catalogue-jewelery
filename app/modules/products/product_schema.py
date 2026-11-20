
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ProductVariantCreate(BaseModel):
    carat: str
    color: str
    size: float
    style: Optional[str] = None
    weight: float


class ProductCreate(BaseModel):
    product_id: str
    metal: str
    product_type: str
    project: str

    category: str
    sub_category: str

    collection: str
    sub_collection: str

    keywords: list[str] = Field(default_factory=list)
    gender: str

    default_carat: str
    default_color: str
    default_size: float
    default_style: Optional[str] = None
    default_weight: float

    wastage: float
    uom: str

    variants: list[ProductVariantCreate] = Field(
        default_factory=list
    )


class ProductVariantResponse(ProductVariantCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(BaseModel):
    id: int
    product_id: str
    metal: str
    product_type: str
    project: str
    category: str
    sub_category: str
    collection: str
    sub_collection: str
    keywords: list[str]
    gender: str

    default_carat: str
    default_color: str
    default_size: float
    default_style: Optional[str]
    default_weight: float
    wastage: float
    uom: str

    variants: list[ProductVariantResponse]

    model_config = ConfigDict(from_attributes=True)
