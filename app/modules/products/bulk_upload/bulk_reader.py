
from io import BytesIO

from fastapi import HTTPException
from openpyxl import load_workbook

from app.modules.products.bulk_upload.bulk_template import (
    PRODUCT_COLUMNS,
    VARIANT_COLUMNS,
)


def read_bulk_workbook(file_content: bytes):
    """
    Read and validate the Product Bulk Upload Excel workbook.

    Returns:
        {
            "products": [
                {
                    "row_number": 2,
                    "data": {...}
                }
            ],
            "variants": [
                {
                    "row_number": 2,
                    "data": {...}
                }
            ]
        }
    """

    try:
        workbook = load_workbook(
            filename=BytesIO(file_content),
            read_only=True,
            data_only=True
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Excel file. Please upload a valid .xlsx workbook."
        )

    try:
        required_sheets = ["Products", "Variants"]

        for sheet_name in required_sheets:
            if sheet_name not in workbook.sheetnames:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required worksheet: {sheet_name}"
                )

        products_ws = workbook["Products"]
        variants_ws = workbook["Variants"]

        validate_headers(
            products_ws,
            PRODUCT_COLUMNS,
            "Products"
        )

        validate_headers(
            variants_ws,
            VARIANT_COLUMNS,
            "Variants"
        )

        products = read_sheet_rows(
            products_ws,
            PRODUCT_COLUMNS
        )

        variants = read_sheet_rows(
            variants_ws,
            VARIANT_COLUMNS
        )

        return {
            "products": products,
            "variants": variants
        }

    finally:
        workbook.close()


def validate_headers(ws, expected_columns, sheet_name):
    actual_columns = [
        cell.value
        for cell in next(
            ws.iter_rows(
                min_row=1,
                max_row=1
            )
        )
    ]

    actual_columns = actual_columns[:len(expected_columns)]

    if actual_columns != expected_columns:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Invalid headers in {sheet_name} worksheet.",
                "expected": expected_columns,
                "received": actual_columns
            }
        )


def read_sheet_rows(ws, columns):
    rows = []

    for row_number, values in enumerate(
        ws.iter_rows(
            min_row=2,
            values_only=True
        ),
        start=2
    ):

        data = {
            column: value
            for column, value in zip(columns, values)
        }

        # Ignore completely empty rows.
        if all(
            value is None or str(value).strip() == ""
            for value in data.values()
        ):
            continue

        rows.append({
            "row_number": row_number,
            "data": data
        })

    return rows
