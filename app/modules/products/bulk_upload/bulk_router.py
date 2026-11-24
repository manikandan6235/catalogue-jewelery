
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db

from app.modules.products.bulk_upload.bulk_template import (
    create_product_template
)

from app.modules.products.bulk_upload.bulk_validation import (
    validate_bulk_workbook
)

from app.modules.products.bulk_upload.bulk_schema import (
    BulkPreviewResponse
)


router = APIRouter(
    prefix="/api/products/bulk",
    tags=["Product Bulk Upload"]
)


# --------------------------------------------------
# DOWNLOAD EXCEL TEMPLATE
# --------------------------------------------------

@router.get("/template")
def download_product_template(
    db: Session = Depends(get_db)
):
    excel_file = create_product_template(db)

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="Product_Bulk_Upload_Template.xlsx"'
        }
    )


# --------------------------------------------------
# PREVIEW BULK PRODUCT UPLOAD
# --------------------------------------------------

@router.post(
    "/preview",
    response_model=BulkPreviewResponse
)
def preview_product_bulk_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # 1. Validate file extension
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx Excel files are supported."
        )

    # 2. Read uploaded file
    file_content = file.file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded Excel file is empty."
        )

    # 3. Execute workbook validation
    result = validate_bulk_workbook(
        db,
        file_content
    )

    # 4. Count valid and invalid products
    valid_products = sum(
        1
        for product in result["products"]
        if product["is_valid"]
    )

    invalid_products = (
        result["total_products"] - valid_products
    )

    # 5. Count valid and invalid variants
    valid_variants = sum(
        1
        for variant in result["variants"]
        if not variant["errors"]
    )

    invalid_variants = (
        result["total_variants"] - valid_variants
    )

    # 6. Return preview response
    return BulkPreviewResponse(
        total_products=result["total_products"],
        total_variants=result["total_variants"],
        valid_products=valid_products,
        invalid_products=invalid_products,
        valid_variants=valid_variants,
        invalid_variants=invalid_variants,
        errors=result["errors"]
    )
