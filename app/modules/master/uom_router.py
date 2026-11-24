
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.uom_schema import (
    UOMCreate,
    UOMUpdate,
    UOMStatusUpdate,
    UOMResponse,
)
from app.modules.master import uom_service


router = APIRouter(
    prefix="/api/masters/uoms",
    tags=["UOM Master"]
)


@router.post("/", response_model=UOMResponse, status_code=status.HTTP_201_CREATED)
def create_uom(
    data: UOMCreate,
    db: Session = Depends(get_db)
):
    return uom_service.create_uom(db, data)


@router.get("/", response_model=list[UOMResponse])
def get_uoms(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    return uom_service.get_uoms(db, active_only)


@router.get("/{uom_id}", response_model=UOMResponse)
def get_uom(
    uom_id: int,
    db: Session = Depends(get_db)
):
    return uom_service.get_uom_by_id(db, uom_id)


@router.put("/{uom_id}", response_model=UOMResponse)
def update_uom(
    uom_id: int,
    data: UOMUpdate,
    db: Session = Depends(get_db)
):
    return uom_service.update_uom(db, uom_id, data)


@router.patch("/{uom_id}/status", response_model=UOMResponse)
def update_uom_status(
    uom_id: int,
    data: UOMStatusUpdate,
    db: Session = Depends(get_db)
):
    return uom_service.update_uom_status(
        db,
        uom_id,
        data.is_active
    )
