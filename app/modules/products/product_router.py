
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
