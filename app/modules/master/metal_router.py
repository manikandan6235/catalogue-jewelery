
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.modules.master.metal_schema import (
    MetalCreate,
    MetalUpdate,
    MetalResponse
)

from app.modules.master import metal_service


router = APIRouter(
    prefix="/masters/metals",
    tags=["Metal Master"]
)


@router.post(
    "/",
    response_model=MetalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_metal(
    data: MetalCreate,
    db: Session = Depends(get_db)
):
    return metal_service.create_metal(db, data)


@router.get(
    "/",
    response_model=list[MetalResponse]
)
def get_metals(
    db: Session = Depends(get_db)
):
    return metal_service.get_metals(db)


@router.get(
    "/{metal_id}",
    response_model=MetalResponse
)
def get_metal(
    metal_id: int,
    db: Session = Depends(get_db)
):
    return metal_service.get_metal(db, metal_id)


@router.put(
    "/{metal_id}",
    response_model=MetalResponse
)
def update_metal(
    metal_id: int,
    data: MetalUpdate,
    db: Session = Depends(get_db)
):
    return metal_service.update_metal(
        db, metal_id, data
    )


@router.patch(
    "/{metal_id}/deactivate",
    response_model=MetalResponse
)
def deactivate_metal(
    metal_id: int,
    db: Session = Depends(get_db)
):
    return metal_service.deactivate_metal(
        db, metal_id
    )
