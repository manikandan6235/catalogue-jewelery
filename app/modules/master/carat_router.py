
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.carat_schema import (
    CaratCreate,
    CaratUpdate,
    CaratStatusUpdate,
    CaratResponse,
)
from app.modules.master import carat_service


router = APIRouter(
    prefix="/api/masters/carats",
    tags=["Carat Master"],
)


@router.post(
    "/",
    response_model=CaratResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_carat(
    data: CaratCreate,
    db: Session = Depends(get_db),
):
    return carat_service.create_carat(db, data)


@router.get(
    "/",
    response_model=list[CaratResponse],
)
def get_carats(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return carat_service.get_carats(db, active_only=active_only)


@router.get(
    "/{carat_id}",
    response_model=CaratResponse,
)
def get_carat(
    carat_id: int,
    db: Session = Depends(get_db),
):
    return carat_service.get_carat(db, carat_id)


@router.put(
    "/{carat_id}",
    response_model=CaratResponse,
)
def update_carat(
    carat_id: int,
    data: CaratUpdate,
    db: Session = Depends(get_db),
):
    return carat_service.update_carat(db, carat_id, data)


@router.patch(
    "/{carat_id}/status",
    response_model=CaratResponse,
)
def update_carat_status(
    carat_id: int,
    data: CaratStatusUpdate,
    db: Session = Depends(get_db),
):
    return carat_service.update_carat_status(db, carat_id, data)
