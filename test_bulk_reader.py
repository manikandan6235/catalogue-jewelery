
from app.modules.products.bulk_upload.bulk_reader import (
    read_bulk_workbook
)

file_path = "Product_Bulk_Upload_Template.xlsx"

with open(file_path, "rb") as file:
    content = file.read()

result = read_bulk_workbook(content)

print("Products:", len(result["products"]))
print("Variants:", len(result["variants"]))

print("Workbook reading successful!")
