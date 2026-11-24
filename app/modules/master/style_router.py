
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.style_schema import (
    StyleCreate,
    StyleUpdate,
    StyleStatusUpdate,
    StyleResponse,
)
from app.modules.master import style_service


router = APIRouter(
    prefix="/api/masters/styles",
    tags=["Style Master"],
)


@router.post("/", response_model=StyleResponse, status_code=201)
def create_style(
    data: StyleCreate,
    db: Session = Depends(get_db),
):
    return style_service.create_style(db, data)


@router.get("/", response_model=list[StyleResponse])
def get_styles(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return style_service.get_styles(db, active_only=active_only)


@router.get("/{style_id}", response_model=StyleResponse)
def get_style(
    style_id: int,
    db: Session = Depends(get_db),
):
    return style_service.get_style(db, style_id)


@router.put("/{style_id}", response_model=StyleResponse)
def update_style(
    style_id: int,
    data: StyleUpdate,
    db: Session = Depends(get_db),
):
    return style_service.update_style(db, style_id, data)


@router.patch("/{style_id}/status", response_model=StyleResponse)
def update_style_status(
    style_id: int,
    data: StyleStatusUpdate,
    db: Session = Depends(get_db),
):
    return style_service.update_style_status(db, style_id, data)
