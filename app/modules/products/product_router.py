
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.products.bulk_upload.bulk_schema import BulkPreviewResponse
from app.modules.products.bulk_upload.bulk_template import create_product_template
from app.modules.products.bulk_upload.bulk_validation import validate_bulk_workbook


from app.database import get_db
from app.modules.products.product_schema import ProductCreate, ProductResponse
from app.modules.products.product_service import create_product

router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.post("/", response_model=ProductResponse)
def add_product(
    data: ProductCreate,
    db: Session = Depends(get_db)
):
    return create_product(db, data)

@router.post("/preview", response_model=BulkPreviewResponse)
def preview_product_bulk_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate uploaded file extension
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx Excel files are supported."
        )

    # Read uploaded Excel file
    file_content = file.file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded Excel file is empty."
        )

    # Run existing validation service
    result = validate_bulk_workbook(db, file_content)

    # Count valid and invalid product groups
    valid_products = sum(
        1 for product in result["products"]
        if product["is_valid"]
    )

    invalid_products = (
        result["total_products"] - valid_products
    )

    # Count valid and invalid variant rows
    valid_variants = sum(
        1 for variant in result["variants"]
        if not variant["errors"]
    )

    invalid_variants = (
        result["total_variants"] - valid_variants
    )

    return BulkPreviewResponse(
        total_products=result["total_products"],
        total_variants=result["total_variants"],
        valid_products=valid_products,
        invalid_products=invalid_products,
        valid_variants=valid_variants,
        invalid_variants=invalid_variants,
        errors=result["errors"]
    )
