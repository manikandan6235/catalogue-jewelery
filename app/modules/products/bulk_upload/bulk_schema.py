
from pydantic import BaseModel, Field


class BulkRowError(BaseModel):
    sheet: str
    row_number: int
    product_id: str | None = None
    column: str | None = None
    message: str


class BulkPreviewResponse(BaseModel):
    total_products: int
    total_variants: int

    valid_products: int
    invalid_products: int

    valid_variants: int
    invalid_variants: int

    errors: list[BulkRowError] = Field(default_factory=list)


class BulkImportResponse(BaseModel):
    total_products: int
    imported_products: int
    failed_products: int

    total_variants: int
    imported_variants: int

    errors: list[BulkRowError] = Field(default_factory=list)
