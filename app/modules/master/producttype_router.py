
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.modules.master.producttype_schema import (
    ProductTypeCreate,
    ProductTypeUpdate,
    ProductTypeResponse
)

from app.modules.master import producttype_service


router = APIRouter(
    prefix="/masters/product-types",
    tags=["Product Type Master"]
)


@router.post(
    "/",
    response_model=ProductTypeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product_type(
    data: ProductTypeCreate,
    db: Session = Depends(get_db)
):
    return producttype_service.create_product_type(db, data)


@router.get(
    "/",
    response_model=list[ProductTypeResponse]
)
def get_product_types(
    db: Session = Depends(get_db)
):
    return producttype_service.get_product_types(db)


@router.get(
    "/{product_type_id}",
    response_model=ProductTypeResponse
)
def get_product_type(
    product_type_id: int,
    db: Session = Depends(get_db)
):
    return producttype_service.get_product_type(
        db, product_type_id
    )


@router.put(
    "/{product_type_id}",
    response_model=ProductTypeResponse
)
def update_product_type(
    product_type_id: int,
    data: ProductTypeUpdate,
    db: Session = Depends(get_db)
):
    return producttype_service.update_product_type(
        db, product_type_id, data
    )


@router.patch(
    "/{product_type_id}/deactivate",
    response_model=ProductTypeResponse
)
def deactivate_product_type(
    product_type_id: int,
    db: Session = Depends(get_db)
):
    return producttype_service.deactivate_product_type(
        db, product_type_id
    )
