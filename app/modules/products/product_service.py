
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.products.product import Product
from app.modules.products.product_variant import ProductVariant
from app.modules.products.product_schema import ProductCreate

from app.modules.master.master import (
    Metal,
    Project,
    ProductType,
    Category,
    Subcategory,
    Collection,
    Subcollection,
    Gender,
    UOM,
    Carat,
    Color,
    Size,
    Style,
)

from app.modules.master.category_attribute_config import (
    CategoryAttributeConfig,
)


# --------------------------------------------------
# MASTER VALIDATION CONFIGURATION
# --------------------------------------------------

MASTER_FIELDS = {
    "metal_id": Metal,
    "project_id": Project,
    "product_type_id": ProductType,
    "category_id": Category,
    "subcategory_id": Subcategory,
    "collection_id": Collection,
    "subcollection_id": Subcollection,
    "gender_id": Gender,
    "uom_id": UOM,
}


ATTRIBUTE_FIELDS = {
    "CARAT": {
        "default_field": "default_carat_id",
        "variant_field": "carat_id",
        "master": Carat,
    },
    "COLOR": {
        "default_field": "default_color_id",
        "variant_field": "color_id",
        "master": Color,
    },
    "SIZE": {
        "default_field": "default_size_id",
        "variant_field": "size_id",
        "master": Size,
    },
    "STYLE": {
        "default_field": "default_style_id",
        "variant_field": "style_id",
        "master": Style,
    },
}


# --------------------------------------------------
# VALIDATE MASTER RECORDS
# --------------------------------------------------

def validate_master_records(db: Session, data: ProductCreate):

    for field_name, model in MASTER_FIELDS.items():

        record_id = getattr(data, field_name)

        record = db.get(model, record_id)

        if record is None:
            raise HTTPException(
                status_code=404,
                detail=f"{field_name} {record_id} does not exist"
            )

        if not record.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} {record_id} is inactive"
            )

    # Validate category and subcategory relationship
    subcategory = db.get(Subcategory, data.subcategory_id)

    if subcategory.category_id != data.category_id:
        raise HTTPException(
            status_code=400,
            detail="Selected subcategory does not belong to the selected category"
        )

    # Validate collection and subcollection relationship
    subcollection = db.get(
        Subcollection,
        data.subcollection_id
    )

    if subcollection.collection_id != data.collection_id:
        raise HTTPException(
            status_code=400,
            detail="Selected subcollection does not belong to the selected collection"
        )


# --------------------------------------------------
# VALIDATE CATEGORY ATTRIBUTE CONFIGURATION
# --------------------------------------------------

def validate_category_attributes(db: Session, data: ProductCreate):

    configurations = db.scalars(
        select(CategoryAttributeConfig).where(
            CategoryAttributeConfig.category_id == data.category_id
        )
    ).all()

    config_map = {
        config.attribute_name: config
        for config in configurations
    }

    for attribute_name, fields in ATTRIBUTE_FIELDS.items():

        config = config_map.get(attribute_name)

        if config is None or not config.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"{attribute_name} configuration is missing or inactive for this category"
            )

        default_value = getattr(
            data,
            fields["default_field"]
        )

        # Product default applicability validation
        if (
            not config.product_default_applicable
            and default_value is not None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{attribute_name} is not applicable as a product default for this category"
            )

        # Product default required validation
        if (
            config.product_default_required
            and default_value is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{attribute_name} is required for this product category"
            )

        # Validate selected attribute master
        if default_value is not None:

            attribute_record = db.get(
                fields["master"],
                default_value
            )

            if attribute_record is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Selected {attribute_name} does not exist"
                )

            if not attribute_record.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Selected {attribute_name} is inactive"
                )

        # Every product must have a first variant.
        # Therefore, a required variant attribute must have
        # a corresponding value in the product defaults.
        if (
            config.variant_applicable
            and config.variant_required
            and default_value is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{attribute_name} is required for the first variant but no product default value was provided"
            )

    return config_map


# --------------------------------------------------
# CREATE INITIAL VARIANT
# --------------------------------------------------

def create_initial_variant(
    product: Product,
    data: ProductCreate,
    config_map: dict
):

    variant_data = {}

    for attribute_name, fields in ATTRIBUTE_FIELDS.items():

        config = config_map[attribute_name]

        default_value = getattr(
            data,
            fields["default_field"]
        )

        if config.variant_applicable:
            variant_data[fields["variant_field"]] = default_value
        else:
            variant_data[fields["variant_field"]] = None

    variant = ProductVariant(
        product_id=product.id,
        **variant_data,
        gross_weight=data.default_gross_weight,
        net_weight=data.default_net_weight,
    )

    return variant


# --------------------------------------------------
# CREATE PRODUCT
# --------------------------------------------------

def create_product(db: Session, data: ProductCreate):

    try:

        # 1. Check duplicate Product ID
        existing = db.scalar(
            select(Product).where(
                Product.product_id == data.product_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Product ID already exists"
            )

        # 2. Validate all master records
        validate_master_records(db, data)

        # 3. Validate category attribute configuration
        config_map = validate_category_attributes(
            db,
            data
        )

        # 4. Validate weights
        if data.default_gross_weight < data.default_net_weight:
            raise HTTPException(
                status_code=400,
                detail="Gross weight must be greater than or equal to net weight"
            )

        # 5. Prepare product data
        product_data = data.model_dump()

        product = Product(**product_data)

        db.add(product)

        # Generate Product ID before creating its variant
        db.flush()

        # 6. Automatically create first variant
        variant = create_initial_variant(
            product,
            data,
            config_map
        )

        db.add(variant)

        # 7. Commit product and variant together
        db.commit()

        # 8. Fetch product with its variants
        created_product = db.scalar(
            select(Product)
            .options(selectinload(Product.variants))
            .where(Product.id == product.id)
        )

        return created_product

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Product creation failed due to a database constraint or duplicate value"
        )

    except Exception:
        db.rollback()
        raise
