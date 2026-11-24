
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Carat
from app.modules.master.carat_schema import (
    CaratCreate,
    CaratUpdate,
    CaratStatusUpdate,
)


def create_carat(db: Session, data: CaratCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Carat code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Carat).where(Carat.code == code)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Carat code already exists.",
        )

    carat = Carat(
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(carat)
        db.commit()
        db.refresh(carat)
        return carat

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Carat code already exists or violates a database constraint.",
        )


def get_carats(db: Session, active_only: bool = False):
    query = select(Carat)

    if active_only:
        query = query.where(Carat.is_active.is_(True))

    return db.scalars(query.order_by(Carat.id)).all()


def get_carat(db: Session, carat_id: int):
    carat = db.get(Carat, carat_id)

    if not carat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carat not found.",
        )

    return carat


def update_carat(db: Session, carat_id: int, data: CaratUpdate):
    carat = get_carat(db, carat_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Carat code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Carat).where(
            Carat.code == code,
            Carat.id != carat_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Carat code already exists.",
        )

    carat.code = code
    carat.name = name

    try:
        db.commit()
        db.refresh(carat)
        return carat

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Carat update violates a database constraint.",
        )


def update_carat_status(
    db: Session,
    carat_id: int,
    data: CaratStatusUpdate,
):
    carat = get_carat(db, carat_id)

    carat.is_active = data.is_active

    db.commit()
    db.refresh(carat)

    return carat
