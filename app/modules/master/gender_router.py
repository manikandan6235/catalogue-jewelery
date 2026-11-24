
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.master.gender_schema import (
    GenderCreate,
    GenderUpdate,
    GenderStatusUpdate,
    GenderResponse,
)
from app.modules.master import gender_service


router = APIRouter(
    prefix="/api/masters/genders",
    tags=["Gender Master"],
)


@router.post("/", response_model=GenderResponse, status_code=201)
def create_gender(
    data: GenderCreate,
    db: Session = Depends(get_db),
):
    return gender_service.create_gender(db, data)


@router.get("/", response_model=list[GenderResponse])
def get_genders(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return gender_service.get_genders(db, active_only=active_only)


@router.get("/{gender_id}", response_model=GenderResponse)
def get_gender(
    gender_id: int,
    db: Session = Depends(get_db),
):
    return gender_service.get_gender(db, gender_id)


@router.put("/{gender_id}", response_model=GenderResponse)
def update_gender(
    gender_id: int,
    data: GenderUpdate,
    db: Session = Depends(get_db),
):
    return gender_service.update_gender(db, gender_id, data)


@router.patch("/{gender_id}/status", response_model=GenderResponse)
def update_gender_status(
    gender_id: int,
    data: GenderStatusUpdate,
    db: Session = Depends(get_db),
):
    return gender_service.update_gender_status(db, gender_id, data)
