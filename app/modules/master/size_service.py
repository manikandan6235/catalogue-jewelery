
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Size
from app.modules.master.size_schema import (
    SizeCreate,
    SizeUpdate,
    SizeStatusUpdate,
)


def create_size(db: Session, data: SizeCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Size).where(Size.code == code)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Size code already exists.",
        )

    size = Size(
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(size)
        db.commit()
        db.refresh(size)
        return size

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Size code already exists or violates a database constraint.",
        )


def get_sizes(db: Session, active_only: bool = False):
    query = select(Size)

    if active_only:
        query = query.where(Size.is_active.is_(True))

    return db.scalars(query.order_by(Size.id)).all()


def get_size(db: Session, size_id: int):
    size = db.get(Size, size_id)

    if not size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Size not found.",
        )

    return size


def update_size(db: Session, size_id: int, data: SizeUpdate):
    size = get_size(db, size_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Size).where(
            Size.code == code,
            Size.id != size_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Size code already exists.",
        )

    size.code = code
    size.name = name

    try:
        db.commit()
        db.refresh(size)
        return size

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Size update violates a database constraint.",
        )


def update_size_status(
    db: Session,
    size_id: int,
    data: SizeStatusUpdate,
):
    size = get_size(db, size_id)

    size.is_active = data.is_active

    db.commit()
    db.refresh(size)

    return size
