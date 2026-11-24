
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.size_schema import (
    SizeCreate,
    SizeUpdate,
    SizeStatusUpdate,
    SizeResponse,
)
from app.modules.master import size_service


router = APIRouter(
    prefix="/api/masters/sizes",
    tags=["Size Master"],
)


@router.post("/", response_model=SizeResponse, status_code=201)
def create_size(
    data: SizeCreate,
    db: Session = Depends(get_db),
):
    return size_service.create_size(db, data)


@router.get("/", response_model=list[SizeResponse])
def get_sizes(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return size_service.get_sizes(db, active_only=active_only)


@router.get("/{size_id}", response_model=SizeResponse)
def get_size(
    size_id: int,
    db: Session = Depends(get_db),
):
    return size_service.get_size(db, size_id)


@router.put("/{size_id}", response_model=SizeResponse)
def update_size(
    size_id: int,
    data: SizeUpdate,
    db: Session = Depends(get_db),
):
    return size_service.update_size(db, size_id, data)


@router.patch("/{size_id}/status", response_model=SizeResponse)
def update_size_status(
    size_id: int,
    data: SizeStatusUpdate,
    db: Session = Depends(get_db),
):
    return size_service.update_size_status(db, size_id, data)
