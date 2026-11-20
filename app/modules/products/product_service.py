
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException

from app.modules.products.product import Product
from app.modules.products.product_variant import ProductVariant
from app.modules.products.product_schema import ProductCreate


def create_product(db: Session, data: ProductCreate):

    existing = db.query(Product).filter(
        Product.product_id == data.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product ID already exists"
        )

    product_data = data.model_dump(exclude={"variants"})

    product = Product(**product_data)

    db.add(product)
    db.flush()

    for variant_data in data.variants:
        variant = ProductVariant(
            product_id=product.id,
            **variant_data.model_dump()
        )
        db.add(variant)

    try:
        db.commit()
        db.refresh(product)
    except Exception:
        db.rollback()
        raise

    return db.query(Product).options(
        selectinload(Product.variants)
    ).filter(Product.id == product.id).first()
