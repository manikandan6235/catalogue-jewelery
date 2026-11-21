
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db

from app.modules.products.bulk_upload.bulk_template import (
    create_product_template
)

router = APIRouter(
    prefix="/api/products/bulk",
    tags=["Product Bulk Upload"]
)


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
