
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName

from app.modules.master.master import (
    Metal, Project, ProductType, Category,
    Subcategory, Collection, Subcollection,
    Gender, UOM, Carat, Color, Size, Style
)


PRODUCT_COLUMNS = [
    "Product_ID", "Metal_Code", "Project_Code",
    "Product_Type_Code", "Category_Code",
    "Subcategory_Code", "Collection_Code",
    "Subcollection_Code", "Gender_Code", "UOM_Code",
    "Default_Carat_Code", "Default_Color_Code",
    "Default_Size_Code", "Default_Style_Code",
    "Default_Gross_Weight", "Default_Net_Weight",
    "Wastage", "Keywords", "Is_Active"
]

VARIANT_COLUMNS = [
    "Product_ID", "Carat_Code", "Color_Code",
    "Size_Code", "Style_Code",
    "Gross_Weight", "Net_Weight"
]


MASTER_MODELS = {
    "Metal_Code": Metal,
    "Project_Code": Project,
    "Product_Type_Code": ProductType,
    "Category_Code": Category,
    "Subcategory_Code": Subcategory,
    "Collection_Code": Collection,
    "Subcollection_Code": Subcollection,
    "Gender_Code": Gender,
    "UOM_Code": UOM,
    "Carat_Code": Carat,
    "Color_Code": Color,
    "Size_Code": Size,
    "Style_Code": Style,
}


def style_worksheet(ws):
    header_fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78"
    )
    header_font = Font(
        bold=True,
        color="FFFFFF",
        size=10
    )

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 25

    for cells in ws.columns:
        letter = get_column_letter(cells[0].column)
        max_length = max(
            len(str(cell.value or ""))
            for cell in cells
        )
        ws.column_dimensions[letter].width = min(
            max(max_length + 4, 16),
            28
        )


def fetch_master_codes(db):
    master_data = {}

    for column_name, model in MASTER_MODELS.items():
        records = (
            db.query(model)
            .filter(model.is_active.is_(True))
            .order_by(model.code)
            .all()
        )

        master_data[column_name] = [
            record.code for record in records
        ]

    return master_data


def add_master_data_sheet(workbook, master_data):
    ws = workbook.create_sheet("MasterData")

    for column_number, (master_name, codes) in enumerate(
        master_data.items(), start=1
    ):
        ws.cell(
            row=1,
            column=column_number,
            value=master_name
        )

        for row_number, code in enumerate(codes, start=2):
            ws.cell(
                row=row_number,
                column=column_number,
                value=code
            )

        # Create a named range for Excel dropdowns.
        if codes:
            letter = get_column_letter(column_number)

            range_formula = (
                f"'MasterData'!${letter}$2:"
                f"${letter}${len(codes) + 1}"
            )

            workbook.defined_names.add(
                DefinedName(
                    name=f"{master_name}_List",
                    attr_text=range_formula
                )
            )

    ws.sheet_state = "hidden"


def add_dropdown(ws, column_number, range_name):
    validation = DataValidation(
        type="list",
        formula1=f"={range_name}",
        allow_blank=True
    )

    validation.errorTitle = "Invalid Master Code"
    validation.error = "Please select a value from the dropdown."
    validation.showErrorMessage = True

    validation.promptTitle = "Select Master Code"
    validation.prompt = "Choose a valid master code."
    validation.showInputMessage = True

    ws.add_data_validation(validation)

    column_letter = get_column_letter(column_number)

    validation.add(
        f"{column_letter}2:{column_letter}1001"
    )


def add_all_dropdowns(workbook):
    products_ws = workbook["Products"]
    variants_ws = workbook["Variants"]

    # Product worksheet dropdowns.
    product_dropdown_columns = {
        "Metal_Code": 2,
        "Project_Code": 3,
        "Product_Type_Code": 4,
        "Category_Code": 5,
        "Subcategory_Code": 6,
        "Collection_Code": 7,
        "Subcollection_Code": 8,
        "Gender_Code": 9,
        "UOM_Code": 10,
        "Default_Carat_Code": 11,
        "Default_Color_Code": 12,
        "Default_Size_Code": 13,
        "Default_Style_Code": 14,
    }

    for master_name, column_number in (
        product_dropdown_columns.items()
    ):
        add_dropdown(
            products_ws,
            column_number,
            f"{master_name}_List"
        )

    # Variant worksheet dropdowns.
    variant_dropdown_columns = {
        "Carat_Code": 2,
        "Color_Code": 3,
        "Size_Code": 4,
        "Style_Code": 5,
    }

    for master_name, column_number in (
        variant_dropdown_columns.items()
    ):
        add_dropdown(
            variants_ws,
            column_number,
            f"{master_name}_List"
        )

    # Is_Active dropdown.
    active_validation = DataValidation(
        type="list",
        formula1='"TRUE,FALSE"',
        allow_blank=True
    )
    active_validation.showErrorMessage = True
    products_ws.add_data_validation(active_validation)
    active_validation.add("S2:S1001")


def create_product_template(db):
    workbook = Workbook()

    # Products worksheet.
    products_ws = workbook.active
    products_ws.title = "Products"
    products_ws.append(PRODUCT_COLUMNS)

    # Variants worksheet.
    variants_ws = workbook.create_sheet("Variants")
    variants_ws.append(VARIANT_COLUMNS)

    # Fetch active master codes from database.
    master_data = fetch_master_codes(db)

    # Create hidden master worksheet.
    add_master_data_sheet(workbook, master_data)

    # Add Excel dropdowns.
    add_all_dropdowns(workbook)

    # Style visible worksheets.
    style_worksheet(products_ws)
    style_worksheet(variants_ws)

    # Text formatting.
    for ws in [products_ws, variants_ws]:
        for row in range(2, 1002):
            for column in range(1, ws.max_column + 1):
                ws.cell(
                    row=row,
                    column=column
                ).number_format = "@"

    # Product weight formatting.
    for row in range(2, 1002):
        for column in [15, 16, 17]:
            products_ws.cell(
                row=row,
                column=column
            ).number_format = "0.000"

        # Variant weights.
        for column in [6, 7]:
            variants_ws.cell(
                row=row,
                column=column
            ).number_format = "0.000"

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output
