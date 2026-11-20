
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.modules.master.master import ProductType
from app.modules.master.producttype_schema import (
    ProductTypeCreate,
    ProductTypeUpdate
)


def create_product_type(db: Session, data: ProductTypeCreate):

    existing = db.scalar(
        select(ProductType).where(
            ProductType.code == data.code
        )
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product type code already exists"
        )

    product_type = ProductType(**data.model_dump())

    try:
        db.add(product_type)
        db.commit()
        db.refresh(product_type)
        return product_type
    except Exception:
        db.rollback()
        raise


def get_product_types(db: Session):

    return db.scalars(
        select(ProductType).order_by(ProductType.id)
    ).all()


def get_product_type(db: Session, product_type_id: int):

    product_type = db.get(ProductType, product_type_id)

    if not product_type:
        raise HTTPException(
            status_code=404,
            detail="Product type not found"
        )

    return product_type


def update_product_type(
    db: Session,
    product_type_id: int,
    data: ProductTypeUpdate
):

    product_type = get_product_type(db, product_type_id)

    update_data = data.model_dump(exclude_unset=True)

    if update_data.get("code") is not None:
        existing = db.scalar(
            select(ProductType).where(
                ProductType.code == update_data["code"],
                ProductType.id != product_type_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Product type code already exists"
            )

    for key, value in update_data.items():
        setattr(product_type, key, value)

    try:
        db.commit()
        db.refresh(product_type)
        return product_type
    except Exception:
        db.rollback()
        raise


def deactivate_product_type(db: Session, product_type_id: int):

    product_type = get_product_type(db, product_type_id)

    product_type.is_active = False

    try:
        db.commit()
        db.refresh(product_type)
        return product_type
    except Exception:
        db.rollback()
        raise
