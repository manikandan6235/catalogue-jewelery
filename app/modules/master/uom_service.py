
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.modules.master.master import UOM


def create_uom(db: Session, data):
    code = data.code.strip().upper()
    name = data.name.strip()

    existing = db.scalar(
        select(UOM).where(UOM.code == code)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"UOM code '{code}' already exists."
        )

    uom = UOM(
        code=code,
        name=name,
        is_active=data.is_active
    )

    try:
        db.add(uom)
        db.commit()
        db.refresh(uom)
        return uom
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"UOM code '{code}' already exists."
        )


def get_uoms(db: Session, active_only: bool = False):
    query = select(UOM).order_by(UOM.id)

    if active_only:
        query = query.where(UOM.is_active.is_(True))

    return db.scalars(query).all()


def get_uom_by_id(db: Session, uom_id: int):
    uom = db.get(UOM, uom_id)

    if not uom:
        raise HTTPException(
            status_code=404,
            detail="UOM not found."
        )

    return uom


def update_uom(db: Session, uom_id: int, data):
    uom = get_uom_by_id(db, uom_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    existing = db.scalar(
        select(UOM).where(
            UOM.code == code,
            UOM.id != uom_id
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"UOM code '{code}' already exists."
        )

    uom.code = code
    uom.name = name

    try:
        db.commit()
        db.refresh(uom)
        return uom
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"UOM code '{code}' already exists."
        )


def update_uom_status(db: Session, uom_id: int, is_active: bool):
    uom = get_uom_by_id(db, uom_id)

    uom.is_active = is_active

    db.commit()
    db.refresh(uom)

    return uom
