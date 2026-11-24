
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.products.product import Product
from decimal import Decimal, InvalidOperation
from app.modules.products.bulk_upload.bulk_reader import read_bulk_workbook

from app.modules.master.category_attribute_config import (
    CategoryAttributeConfig,
)

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


MASTER_CODE_FIELDS = {
    "Metal_Code": ("metal_id", Metal),
    "Project_Code": ("project_id", Project),
    "Product_Type_Code": ("product_type_id", ProductType),
    "Category_Code": ("category_id", Category),
    "Subcategory_Code": ("subcategory_id", Subcategory),
    "Collection_Code": ("collection_id", Collection),
    "Subcollection_Code": ("subcollection_id", Subcollection),
    "Gender_Code": ("gender_id", Gender),
    "UOM_Code": ("uom_id", UOM),
    "Default_Carat_Code": ("default_carat_id", Carat),
    "Default_Color_Code": ("default_color_id", Color),
    "Default_Size_Code": ("default_size_id", Size),
    "Default_Style_Code": ("default_style_id", Style),
}


VARIANT_CODE_FIELDS = {
    "Carat_Code": ("carat_id", Carat),
    "Color_Code": ("color_id", Color),
    "Size_Code": ("size_id", Size),
    "Style_Code": ("style_id", Style),
}


def resolve_master_code(
    db: Session,
    model,
    code: str,
):
    if code is None or str(code).strip() == "":
        return None

    normalized_code = str(code).strip().upper()

    record = db.scalar(
        select(model).where(
            model.code == normalized_code
        )
    )

    if record is None or not record.is_active:
        return None

    return record.id


def validate_product_master_codes(
    db: Session,
    product_data: dict,
    row_number: int,
):
    """
    Resolve Excel master codes into database IDs.

    Returns:
        resolved_data: Dictionary containing database IDs.
        errors: List of validation errors.
    """

    resolved_data = {}
    errors = []

    for excel_column, (db_field, model) in MASTER_CODE_FIELDS.items():

        code = product_data.get(excel_column)

        # Required master fields
        if excel_column in {
            "Metal_Code",
            "Project_Code",
            "Product_Type_Code",
            "Category_Code",
            "Subcategory_Code",
            "Collection_Code",
            "Subcollection_Code",
            "Gender_Code",
            "UOM_Code",
        }:
            if code is None or str(code).strip() == "":
                errors.append({
                    "row_number": row_number,
                    "column": excel_column,
                    "message": f"{excel_column} is required."
                })
                continue

        # Optional attribute fields
        if code is None or str(code).strip() == "":
            resolved_data[db_field] = None
            continue

        normalized_code = str(code).strip().upper()

        master_id = resolve_master_code(
            db,
            model,
            normalized_code
        )

        if master_id is None:
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"Invalid or inactive master code: {normalized_code}"
                )
            })
            continue

        resolved_data[db_field] = master_id

    # Category and subcategory relationship validation
    category_id = resolved_data.get("category_id")
    subcategory_id = resolved_data.get("subcategory_id")

    if category_id is not None and subcategory_id is not None:

        subcategory = db.get(Subcategory, subcategory_id)

        if subcategory.category_id != category_id:
            errors.append({
                "row_number": row_number,
                "column": "Subcategory_Code",
                "message": (
                    "Selected subcategory does not belong "
                    "to the selected category."
                )
            })

    # Collection and subcollection relationship validation
    collection_id = resolved_data.get("collection_id")
    subcollection_id = resolved_data.get("subcollection_id")

    if collection_id is not None and subcollection_id is not None:

        subcollection = db.get(
            Subcollection,
            subcollection_id
        )

        if subcollection.collection_id != collection_id:
            errors.append({
                "row_number": row_number,
                "column": "Subcollection_Code",
                "message": (
                    "Selected subcollection does not belong "
                    "to the selected collection."
                )
            })

    return resolved_data, errors


ATTRIBUTE_CONFIG_FIELDS = {
    "CARAT": ("default_carat_id", "Default_Carat_Code"),
    "COLOR": ("default_color_id", "Default_Color_Code"),
    "SIZE": ("default_size_id", "Default_Size_Code"),
    "STYLE": ("default_style_id", "Default_Style_Code"),
}


def validate_product_attribute_config(
    db: Session,
    category_id: int,
    resolved_data: dict,
    row_number: int,
):
    """
    Validate product default attributes using
    CategoryAttributeConfig.

    Product default rules are independent of variant rules.
    """

    errors = []

    configurations = db.scalars(
        select(CategoryAttributeConfig).where(
            CategoryAttributeConfig.category_id == category_id
        )
    ).all()

    config_map = {
        config.attribute_name: config
        for config in configurations
    }

    for attribute_name, fields in ATTRIBUTE_CONFIG_FIELDS.items():

        db_field, excel_column = fields

        config = config_map.get(attribute_name)

        if config is None:
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"{attribute_name} configuration "
                    "is missing for this category."
                )
            })
            continue

        if not config.is_active:
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"{attribute_name} configuration "
                    "is inactive for this category."
                )
            })
            continue

        default_value = resolved_data.get(db_field)

        # Attribute is not applicable for product defaults.
        if (
            not config.product_default_applicable
            and default_value is not None
        ):
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"{attribute_name} is not applicable "
                    "as a product default for this category."
                )
            })

        # Attribute is mandatory for product defaults.
        if (
            config.product_default_required
            and default_value is None
        ):
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"{attribute_name} is required "
                    "for this product category."
                )
            })

    return errors


def validate_variant_master_codes(
    db: Session,
    variant_data: dict,
    category_id: int,
    row_number: int,
):
    """
    Resolve variant master codes and validate them
    against the product category configuration.
    """

    resolved_data = {}
    errors = []

    configurations = db.scalars(
        select(CategoryAttributeConfig).where(
            CategoryAttributeConfig.category_id == category_id
        )
    ).all()

    config_map = {
        config.attribute_name: config
        for config in configurations
    }

    variant_attributes = {
        "CARAT": ("Carat_Code", "carat_id"),
        "COLOR": ("Color_Code", "color_id"),
        "SIZE": ("Size_Code", "size_id"),
        "STYLE": ("Style_Code", "style_id"),
    }

    for attribute_name, fields in variant_attributes.items():

        excel_column, db_field = fields

        code = variant_data.get(excel_column)

        config = config_map.get(attribute_name)

        # Check configuration
        if config is None or not config.is_active:
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"{attribute_name} configuration is "
                    "missing or inactive for this category."
                )
            })
            continue

        is_empty = (
            code is None or str(code).strip() == ""
        )

        # Check whether attribute is applicable
        if not config.variant_applicable:

            resolved_data[db_field] = None

            if not is_empty:
                errors.append({
                    "row_number": row_number,
                    "column": excel_column,
                    "message": (
                        f"{attribute_name} is not applicable "
                        "for variants in this category."
                    )
                })

            continue

        # Check required attributes
        if config.variant_required and is_empty:
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"{attribute_name} is required "
                    "for variants in this category."
                )
            })

            resolved_data[db_field] = None
            continue

        # Optional attribute can be blank
        if is_empty:
            resolved_data[db_field] = None
            continue

        # Resolve master code
        normalized_code = str(code).strip().upper()

        master_id = resolve_master_code(
            db,
            VARIANT_CODE_FIELDS[excel_column][1],
            normalized_code
        )

        if master_id is None:
            errors.append({
                "row_number": row_number,
                "column": excel_column,
                "message": (
                    f"Invalid or inactive master code: "
                    f"{normalized_code}"
                )
            })
            resolved_data[db_field] = None
            continue

        resolved_data[db_field] = master_id

    return resolved_data, errors


def convert_decimal_value(
    value,
    column_name: str,
    row_number: int,
    sheet_name: str,
    required: bool = True,
    max_integer_digits: int = 9,
):
    """
    Convert an Excel value into Decimal and validate
    its precision for the database Numeric column.
    """

    if value is None or str(value).strip() == "":
        if required:
            return None, {
                "row_number": row_number,
                "column": column_name,
                "message": f"{column_name} is required."
            }

        return Decimal("0.000"), None

    if isinstance(value, bool):
        return None, {
            "row_number": row_number,
            "column": column_name,
            "message": f"{column_name} must be a valid number."
        }

    try:
        number = Decimal(str(value).strip())

    except (InvalidOperation, ValueError):
        return None, {
            "row_number": row_number,
            "column": column_name,
            "message": f"{column_name} must be a valid number."
        }

    if not number.is_finite():
        return None, {
            "row_number": row_number,
            "column": column_name,
            "message": f"{column_name} must be a finite number."
        }

    decimal_places = max(0, -number.as_tuple().exponent)

    integer_digits = max(0, number.adjusted() + 1) if number != 0 else 0

    if decimal_places > 3:
        return None, {
            "row_number": row_number,
            "column": column_name,
            "message": f"{column_name} supports a maximum of 3 decimal places."
        }

    if integer_digits > max_integer_digits:
        return None, {
            "row_number": row_number,
            "column": column_name,
            "message": f"{column_name} exceeds the maximum allowed value."
        }

    return number, None


def validate_weight_values(
    row_data: dict,
    row_number: int,
    sheet_name: str,
):
    """
    Validate product or variant weight fields.

    Returns:
        converted_values, errors
    """

    errors = []
    converted_values = {}

    if sheet_name == "Products":

        fields = {
            "Default_Gross_Weight": {
                "required": True,
                "max_integer_digits": 9,
                "minimum": Decimal("0"),
                "strictly_greater": True,
            },
            "Default_Net_Weight": {
                "required": True,
                "max_integer_digits": 9,
                "minimum": Decimal("0"),
                "strictly_greater": True,
            },
            "Wastage": {
                "required": True,
                "max_integer_digits": 5,
                "minimum": Decimal("0"),
                "strictly_greater": False,
            },
        }

    elif sheet_name == "Variants":

        fields = {
            "Gross_Weight": {
                "required": True,
                "max_integer_digits": 9,
                "minimum": Decimal("0"),
                "strictly_greater": True,
            },
            "Net_Weight": {
                "required": True,
                "max_integer_digits": 9,
                "minimum": Decimal("0"),
                "strictly_greater": True,
            },
        }

    else:
        raise ValueError("Unsupported worksheet name.")

    for column_name, rules in fields.items():

        value, error = convert_decimal_value(
            row_data.get(column_name),
            column_name,
            row_number,
            sheet_name,
            required=rules["required"],
            max_integer_digits=rules["max_integer_digits"],
        )

        if error:
            errors.append(error)
            continue

        if rules["strictly_greater"] and value <= rules["minimum"]:
            errors.append({
                "row_number": row_number,
                "column": column_name,
                "message": f"{column_name} must be greater than zero."
            })
            continue

        if not rules["strictly_greater"] and value < rules["minimum"]:
            errors.append({
                "row_number": row_number,
                "column": column_name,
                "message": f"{column_name} cannot be negative."
            })
            continue

        converted_values[column_name] = value

    # Gross weight must be >= net weight.
    if sheet_name == "Products":
        gross = converted_values.get("Default_Gross_Weight")
        net = converted_values.get("Default_Net_Weight")

    else:
        gross = converted_values.get("Gross_Weight")
        net = converted_values.get("Net_Weight")

    if gross is not None and net is not None and gross < net:
        errors.append({
            "row_number": row_number,
            "column": (
                "Default_Gross_Weight"
                if sheet_name == "Products"
                else "Gross_Weight"
            ),
            "message": (
                "Gross weight must be greater than "
                "or equal to net weight."
            )
        })

    return converted_values, errors


def normalize_product_id(value):
    if value is None:
        return ""

    return str(value).strip()


def validate_duplicate_product_ids(
    db: Session,
    products: list,
):
    """
    Validate duplicate Product IDs within Excel
    and against existing database records.
    """

    errors = []
    product_groups = {}

    # Check duplicate IDs inside the uploaded workbook.
    for item in products:

        row_number = item["row_number"]
        data = item["data"]

        product_id = normalize_product_id(
            data.get("Product_ID")
        )

        if not product_id:
            errors.append({
                "sheet": "Products",
                "row_number": row_number,
                "product_id": None,
                "column": "Product_ID",
                "message": "Product_ID is required."
            })
            continue

        product_groups.setdefault(
            product_id,
            []
        ).append(row_number)

    # Report every row involved in a duplicate.
    for product_id, row_numbers in product_groups.items():

        if len(row_numbers) > 1:

            for row_number in row_numbers:
                errors.append({
                    "sheet": "Products",
                    "row_number": row_number,
                    "product_id": product_id,
                    "column": "Product_ID",
                    "message": (
                        f"Duplicate Product_ID '{product_id}' "
                        "found in the uploaded Excel file."
                    )
                })

    # Check existing product IDs in PostgreSQL.
    uploaded_ids = list(product_groups.keys())

    if uploaded_ids:

        existing_ids = set(
            db.scalars(
                select(Product.product_id).where(
                    Product.product_id.in_(uploaded_ids)
                )
            ).all()
        )

        for product_id in existing_ids:

            for row_number in product_groups[product_id]:
                errors.append({
                    "sheet": "Products",
                    "row_number": row_number,
                    "product_id": product_id,
                    "column": "Product_ID",
                    "message": (
                        f"Product_ID '{product_id}' "
                        "already exists in the database."
                    )
                })

    return errors


def validate_variant_product_references(
    products: list,
    variants: list,
):
    """
    Every variant must reference a product
    present in the Products worksheet.
    """

    errors = []

    product_ids = {
        normalize_product_id(
            item["data"].get("Product_ID")
        )
        for item in products
        if normalize_product_id(
            item["data"].get("Product_ID")
        )
    }

    for item in variants:

        row_number = item["row_number"]
        data = item["data"]

        product_id = normalize_product_id(
            data.get("Product_ID")
        )

        if not product_id:
            errors.append({
                "sheet": "Variants",
                "row_number": row_number,
                "product_id": None,
                "column": "Product_ID",
                "message": "Product_ID is required."
            })

        elif product_id not in product_ids:
            errors.append({
                "sheet": "Variants",
                "row_number": row_number,
                "product_id": product_id,
                "column": "Product_ID",
                "message": (
                    f"Product_ID '{product_id}' does not "
                    "exist in the Products worksheet."
                )
            })

    return errors


def validate_duplicate_variant_combinations(
    variants: list,
):
    """
    Detect duplicate variant combinations within the
    uploaded workbook, including blank attributes.

    Attribute codes are compared case-insensitively.
    """

    errors = []
    combination_groups = {}

    attribute_columns = [
        "Carat_Code",
        "Color_Code",
        "Size_Code",
        "Style_Code",
    ]

    for item in variants:

        row_number = item["row_number"]
        data = item["data"]

        product_id = normalize_product_id(
            data.get("Product_ID")
        )

        if not product_id:
            continue

        attributes = tuple(
            (
                str(data.get(column)).strip().upper()
                if data.get(column) is not None
                and str(data.get(column)).strip()
                else None
            )
            for column in attribute_columns
        )

        combination_key = (
            product_id,
            *attributes
        )

        combination_groups.setdefault(
            combination_key,
            []
        ).append(row_number)

    # Report all rows involved in duplicate combinations.
    for combination_key, row_numbers in combination_groups.items():

        if len(row_numbers) > 1:

            product_id = combination_key[0]

            for row_number in row_numbers:
                errors.append({
                    "sheet": "Variants",
                    "row_number": row_number,
                    "product_id": product_id,
                    "column": "Carat_Code, Color_Code, Size_Code, Style_Code",
                    "message": (
                        "Duplicate variant combination found "
                        f"for product '{product_id}'."
                    )
                })

    return errors




def validate_bulk_workbook(db: Session, file_content: bytes):
    """
    Complete validation for Product Bulk Upload.

    This function only reads and validates data.
    It does not insert or update database records.
    """

    workbook_data = read_bulk_workbook(file_content)

    products = workbook_data["products"]
    variants = workbook_data["variants"]

    all_errors = []

    # --------------------------------------------------
    # Helper: attach worksheet and product information
    # --------------------------------------------------

    def add_errors(
        errors,
        sheet_name,
        product_id=None,
    ):
        formatted_errors = []

        for error in errors:
            formatted = {
                "sheet": error.get("sheet", sheet_name),
                "row_number": error["row_number"],
                "product_id": error.get("product_id", product_id),
                "column": error.get("column"),
                "message": error["message"],
            }

            formatted_errors.append(formatted)
            all_errors.append(formatted)

        return formatted_errors

    # --------------------------------------------------
    # Step 1: Cross-worksheet validations
    # --------------------------------------------------

    duplicate_product_errors = validate_duplicate_product_ids(
        db,
        products,
    )

    reference_errors = validate_variant_product_references(
        products,
        variants,
    )

    duplicate_variant_errors = validate_duplicate_variant_combinations(
        variants,
    )

    # --------------------------------------------------
    # Step 2: Group products by Product_ID
    # --------------------------------------------------

    product_groups = {}

    for item in products:

        product_id = normalize_product_id(
            item["data"].get("Product_ID")
        )

        if product_id:
            product_groups.setdefault(
                product_id,
                []
            ).append(item)

    # --------------------------------------------------
    # Step 3: Validate each product
    # --------------------------------------------------

    validated_products = {}

    for product_id, product_rows in product_groups.items():

        # Duplicate IDs are invalid, so do not treat
        # either row as a valid product.
        if len(product_rows) > 1:
            continue

        item = product_rows[0]

        row_number = item["row_number"]
        raw_data = item["data"]

        product_errors = []

        resolved_data, master_errors = validate_product_master_codes(
            db,
            raw_data,
            row_number,
        )

        product_errors.extend(
            add_errors(
                master_errors,
                "Products",
                product_id,
            )
        )

        # Validate category-based product defaults.
        category_id = resolved_data.get("category_id")

        if category_id is not None:

            config_errors = validate_product_attribute_config(
                db,
                category_id,
                resolved_data,
                row_number,
            )

            product_errors.extend(
                add_errors(
                    config_errors,
                    "Products",
                    product_id,
                )
            )

        # Validate product weights.
        weight_values, weight_errors = validate_weight_values(
            raw_data,
            row_number,
            "Products",
        )

        product_errors.extend(
            add_errors(
                weight_errors,
                "Products",
                product_id,
            )
        )

        validated_products[product_id] = {
            "row_number": row_number,
            "product_id": product_id,
            "raw_data": raw_data,
            "resolved_data": resolved_data,
            "weight_values": weight_values,
            "errors": product_errors,
        }

    # --------------------------------------------------
    # Step 4: Ensure every product has at least one variant
    # --------------------------------------------------

    variant_counts = {}

    for item in variants:

        product_id = normalize_product_id(
            item["data"].get("Product_ID")
        )

        if product_id:
            variant_counts[product_id] = (
                variant_counts.get(product_id, 0) + 1
            )

    for product_id, product in validated_products.items():

        if variant_counts.get(product_id, 0) == 0:

            missing_variant_error = {
                "sheet": "Products",
                "row_number": product["row_number"],
                "product_id": product_id,
                "column": "Product_ID",
                "message": (
                    "At least one variant is required "
                    "for every product."
                ),
            }

            product["errors"].append(missing_variant_error)
            all_errors.append(missing_variant_error)

    # --------------------------------------------------
    # Step 5: Validate each variant
    # --------------------------------------------------

    validated_variants = []

    for item in variants:

        row_number = item["row_number"]
        raw_data = item["data"]

        product_id = normalize_product_id(
            raw_data.get("Product_ID")
        )

        variant_errors = []

        # Attach cross-worksheet reference errors.
        for error in reference_errors:
            if error["row_number"] == row_number:
                variant_errors.extend(
                    add_errors(
                        [error],
                        "Variants",
                        product_id or None,
                    )
                )

        # Attach duplicate variant combination errors.
        for error in duplicate_variant_errors:
            if error["row_number"] == row_number:
                variant_errors.extend(
                    add_errors(
                        [error],
                        "Variants",
                        product_id or None,
                    )
                )

        parent_product = validated_products.get(product_id)

        # Do not validate attribute codes without a valid
        # parent product category.
        if parent_product:

            category_id = parent_product[
                "resolved_data"
            ].get("category_id")

            if category_id is not None:

                resolved_variant_data, master_errors = (
                    validate_variant_master_codes(
                        db,
                        raw_data,
                        category_id,
                        row_number,
                    )
                )

                variant_errors.extend(
                    add_errors(
                        master_errors,
                        "Variants",
                        product_id,
                    )
                )

            else:
                resolved_variant_data = {}

        else:
            resolved_variant_data = {}

        # Validate variant weights.
        weight_values, weight_errors = validate_weight_values(
            raw_data,
            row_number,
            "Variants",
        )

        variant_errors.extend(
            add_errors(
                weight_errors,
                "Variants",
                product_id or None,
            )
        )

        validated_variants.append({
            "row_number": row_number,
            "product_id": product_id,
            "raw_data": raw_data,
            "resolved_data": resolved_variant_data,
            "weight_values": weight_values,
            "errors": variant_errors,
        })

    # --------------------------------------------------
    # Step 6: Attach duplicate Product ID errors
    # --------------------------------------------------

    for error in duplicate_product_errors:
        add_errors(
            [error],
            "Products",
            error.get("product_id"),
        )

    # --------------------------------------------------
    # Step 7: Final validation result
    # --------------------------------------------------

    # A product group is valid only when its product row
    # and every associated variant row are valid.

    product_results = []

    for product_id, product in validated_products.items():

        related_variants = [
            variant
            for variant in validated_variants
            if variant["product_id"] == product_id
        ]

        group_valid = (
            len(product["errors"]) == 0
            and len(related_variants) > 0
            and all(
                len(variant["errors"]) == 0
                for variant in related_variants
            )
        )

        product_results.append({
            **product,
            "variants": related_variants,
            "is_valid": group_valid,
        })

    return {
        "total_products": len(products),
        "total_variants": len(variants),
        "products": product_results,
        "variants": validated_variants,
        "errors": all_errors,
    }
