
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------
# PRODUCT CREATE SCHEMA
# --------------------------------------------------

class ProductCreate(BaseModel):

    # Product identification
    product_id: str = Field(
        min_length=1,
        max_length=50
    )

    # Master table references
    metal_id: int = Field(gt=0)
    project_id: int = Field(gt=0)
    product_type_id: int = Field(gt=0)

    category_id: int = Field(gt=0)
    subcategory_id: int = Field(gt=0)

    collection_id: int = Field(gt=0)
    subcollection_id: int = Field(gt=0)

    gender_id: int = Field(gt=0)
    uom_id: int = Field(gt=0)

    # Default attributes
    # Required/optional status is validated
    # dynamically using category_attribute_config.

    default_carat_id: int | None = Field(default=None, gt=0)
    default_color_id: int | None = Field(default=None, gt=0)
    default_size_id: int | None = Field(default=None, gt=0)
    default_style_id: int | None = Field(default=None, gt=0)

    # Default weights
    default_gross_weight: Decimal = Field(gt=0)
    default_net_weight: Decimal = Field(gt=0)

    # Other product details
    wastage: Decimal = Field(ge=0)

    keywords: list[str] = Field(
        default_factory=list
    )

    is_active: bool = True


# --------------------------------------------------
# PRODUCT VARIANT RESPONSE SCHEMA
# --------------------------------------------------

class ProductVariantResponse(BaseModel):

    id: int
    product_id: int

    carat_id: int | None
    color_id: int | None
    size_id: int | None
    style_id: int | None

    gross_weight: Decimal
    net_weight: Decimal

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# PRODUCT RESPONSE SCHEMA
# --------------------------------------------------

class ProductResponse(BaseModel):

    id: int
    product_id: str

    # Master IDs
    metal_id: int
    project_id: int
    product_type_id: int

    category_id: int
    subcategory_id: int

    collection_id: int
    subcollection_id: int

    gender_id: int
    uom_id: int

    # Default attributes
    default_carat_id: int | None
    default_color_id: int | None
    default_size_id: int | None
    default_style_id: int | None

    # Default weights
    default_gross_weight: Decimal
    default_net_weight: Decimal

    # Other details
    wastage: Decimal
    keywords: list[str]
    is_active: bool

    # Automatically generated variants
    variants: list[ProductVariantResponse]

    model_config = ConfigDict(from_attributes=True)
