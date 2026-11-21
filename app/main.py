from fastapi import FastAPI

from app.core.config import settings
from app.database.session import engine
from app.database.init_db import create_tables

from app.modules.products.product_router import router as product_router
from app.modules.master.metal_router import router as metal_router
from app.modules.master.project_router import router as project_router
from app.modules.master.producttype_router import router as product_type_router
from app.modules.products.bulk_upload.bulk_router import router as bulk_router
from app.modules.master.category_router import router as category_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)



@app.on_event("startup")
def startup():
    create_tables()
app.include_router(product_router)
app.include_router(metal_router)
app.include_router(project_router)
app.include_router(product_type_router)
app.include_router(bulk_router)
app.include_router(category_router)


@app.get("/")
def home():
    return {
        "message": "Ecommerce API is running"
    }


@app.get("/health")
def health_check():

    try:
        with engine.connect():
            return {
                "status": "healthy",
                "database": "connected"
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
