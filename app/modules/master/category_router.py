
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db

from app.modules.master.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryStatusUpdate,
    CategoryResponse
)

from app.modules.master.category_service import (
    get_categories,
    get_category_by_id,
    create_category,
    update_category,
    update_category_status
)


router = APIRouter(
    prefix="/api/masters/categories",
    tags=["Category Master"]
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=201
)
def add_category(
    data: CategoryCreate,
    db: Session = Depends(get_db)
):
    return create_category(db, data)


@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def list_categories(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    return get_categories(db, active_only)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    return get_category_by_id(db, category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def edit_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    return update_category(db, category_id, data)


@router.patch(
    "/{category_id}/status",
    response_model=CategoryResponse
)
def change_category_status(
    category_id: int,
    data: CategoryStatusUpdate,
    db: Session = Depends(get_db)
):
    return update_category_status(
        db,
        category_id,
        data.is_active
    )
