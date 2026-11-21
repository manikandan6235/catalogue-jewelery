
from app.database.base import Base
from app.database.session import engine

# Import all models before create_all
from app.modules.master import master
from app.modules.products import product
from app.modules.products import product_variant
from app.modules.master import category_attribute_config


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("All jewellery ERP tables created successfully!")
