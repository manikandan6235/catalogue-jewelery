
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.subcategory_Schema import (
    SubcategoryCreate,
    SubcategoryUpdate,
    SubcategoryStatusUpdate,
    SubcategoryResponse,
)
from app.modules.master import subcategory_service


router = APIRouter(
    prefix="/api/masters/subcategories",
    tags=["Subcategory Master"],
)


@router.post(
    "/",
    response_model=SubcategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subcategory(
    data: SubcategoryCreate,
    db: Session = Depends(get_db),
):
    return subcategory_service.create_subcategory(db, data)


@router.get(
    "/",
    response_model=list[SubcategoryResponse],
)
def get_subcategories(
    category_id: int | None = Query(default=None, gt=0),
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return subcategory_service.get_subcategories(
        db,
        category_id=category_id,
        active_only=active_only,
    )


@router.get(
    "/{subcategory_id}",
    response_model=SubcategoryResponse,
)
def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
):
    return subcategory_service.get_subcategory(db, subcategory_id)


@router.put(
    "/{subcategory_id}",
    response_model=SubcategoryResponse,
)
def update_subcategory(
    subcategory_id: int,
    data: SubcategoryUpdate,
    db: Session = Depends(get_db),
):
    return subcategory_service.update_subcategory(
        db,
        subcategory_id,
        data,
    )


@router.patch(
    "/{subcategory_id}/status",
    response_model=SubcategoryResponse,
)
def update_subcategory_status(
    subcategory_id: int,
    data: SubcategoryStatusUpdate,
    db: Session = Depends(get_db),
):
    return subcategory_service.update_subcategory_status(
        db,
        subcategory_id,
        data,
    )
