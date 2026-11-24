import app.database.init_db
from app.database import get_db
from app.modules.products.bulk_upload.bulk_validation import (
    validate_bulk_workbook,
)

file_path = "Product_Bulk_Upload_Template.xlsx"

# Read the Excel file.
with open(file_path, "rb") as file:
    file_content = file.read()

# Get a database session using the existing dependency.
db_generator = get_db()
db = next(db_generator)

try:
    result = validate_bulk_workbook(db, file_content)

    print("\n========== BULK VALIDATION RESULT ==========")

    print("Total Products:", result["total_products"])
    print("Total Variants:", result["total_variants"])

    print("Validated Product Groups:", len(result["products"]))
    print("Validated Variant Rows:", len(result["variants"]))

    print("\n========== PRODUCT STATUS ==========")

    for product in result["products"]:
        print(
            product["product_id"],
            "->",
            "VALID" if product["is_valid"] else "INVALID",
        )

    print("\n========== VALIDATION ERRORS ==========")

    if result["errors"]:
        for error in result["errors"]:
            print(
                f'{error["sheet"]} | '
                f'Row {error["row_number"]} | '
                f'{error.get("product_id")} | '
                f'{error.get("column")} | '
                f'{error["message"]}'
            )
    else:
        print("No validation errors found.")

    print("\n===========================================")

finally:
    db.close()
    try:
        next(db_generator)
    except StopIteration:
        pass
