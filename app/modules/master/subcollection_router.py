
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.subcollection_schema import (
    SubcollectionCreate,
    SubcollectionUpdate,
    SubcollectionStatusUpdate,
    SubcollectionResponse,
)
from app.modules.master import subcollection_service


router = APIRouter(
    prefix="/api/masters/subcollections",
    tags=["Subcollection Master"],
)


@router.post(
    "/",
    response_model=SubcollectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subcollection(
    data: SubcollectionCreate,
    db: Session = Depends(get_db),
):
    return subcollection_service.create_subcollection(db, data)


@router.get(
    "/",
    response_model=list[SubcollectionResponse],
)
def get_subcollections(
    collection_id: int | None = Query(default=None, gt=0),
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return subcollection_service.get_subcollections(
        db,
        collection_id=collection_id,
        active_only=active_only,
    )


@router.get(
    "/{subcollection_id}",
    response_model=SubcollectionResponse,
)
def get_subcollection(
    subcollection_id: int,
    db: Session = Depends(get_db),
):
    return subcollection_service.get_subcollection(db, subcollection_id)


@router.put(
    "/{subcollection_id}",
    response_model=SubcollectionResponse,
)
def update_subcollection(
    subcollection_id: int,
    data: SubcollectionUpdate,
    db: Session = Depends(get_db),
):
    return subcollection_service.update_subcollection(
        db,
        subcollection_id,
        data,
    )


@router.patch(
    "/{subcollection_id}/status",
    response_model=SubcollectionResponse,
)
def update_subcollection_status(
    subcollection_id: int,
    data: SubcollectionStatusUpdate,
    db: Session = Depends(get_db),
):
    return subcollection_service.update_subcollection_status(
        db,
        subcollection_id,
        data,
    )
