
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.modules.master.master import Metal
from app.modules.master.metal_schema import (
    MetalCreate,
    MetalUpdate
)


def create_metal(db: Session, data: MetalCreate):

    existing = db.scalar(
        select(Metal).where(Metal.code == data.code)
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Metal code already exists"
        )

    metal = Metal(**data.model_dump())

    try:
        db.add(metal)
        db.commit()
        db.refresh(metal)
        return metal
    except Exception:
        db.rollback()
        raise


def get_metals(db: Session):

    return db.scalars(
        select(Metal).order_by(Metal.id)
    ).all()


def get_metal(db: Session, metal_id: int):

    metal = db.get(Metal, metal_id)

    if not metal:
        raise HTTPException(
            status_code=404,
            detail="Metal not found"
        )

    return metal


def update_metal(
    db: Session,
    metal_id: int,
    data: MetalUpdate
):

    metal = get_metal(db, metal_id)

    update_data = data.model_dump(exclude_unset=True)

    if update_data.get("code") is not None:
        existing = db.scalar(
            select(Metal).where(
                Metal.code == update_data["code"],
                Metal.id != metal_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Metal code already exists"
            )

    for key, value in update_data.items():
        setattr(metal, key, value)

    try:
        db.commit()
        db.refresh(metal)
        return metal
    except Exception:
        db.rollback()
        raise


def deactivate_metal(db: Session, metal_id: int):

    metal = get_metal(db, metal_id)

    metal.is_active = False

    try:
        db.commit()
        db.refresh(metal)
        return metal
    except Exception:
        db.rollback()
        raise
