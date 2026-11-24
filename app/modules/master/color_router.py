
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.color_schema import (
    ColorCreate,
    ColorUpdate,
    ColorStatusUpdate,
    ColorResponse,
)
from app.modules.master import color_service


router = APIRouter(
    prefix="/api/masters/colors",
    tags=["Color Master"],
)


@router.post("/", response_model=ColorResponse, status_code=201)
def create_color(
    data: ColorCreate,
    db: Session = Depends(get_db),
):
    return color_service.create_color(db, data)


@router.get("/", response_model=list[ColorResponse])
def get_colors(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return color_service.get_colors(db, active_only=active_only)


@router.get("/{color_id}", response_model=ColorResponse)
def get_color(
    color_id: int,
    db: Session = Depends(get_db),
):
    return color_service.get_color(db, color_id)


@router.put("/{color_id}", response_model=ColorResponse)
def update_color(
    color_id: int,
    data: ColorUpdate,
    db: Session = Depends(get_db),
):
    return color_service.update_color(db, color_id, data)


@router.patch("/{color_id}/status", response_model=ColorResponse)
def update_color_status(
    color_id: int,
    data: ColorStatusUpdate,
    db: Session = Depends(get_db),
):
    return color_service.update_color_status(db, color_id, data)
