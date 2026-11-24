
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Color
from app.modules.master.color_schema import (
    ColorCreate,
    ColorUpdate,
    ColorStatusUpdate,
)


def create_color(db: Session, data: ColorCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Color code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Color).where(Color.code == code)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Color code already exists.",
        )

    color = Color(
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(color)
        db.commit()
        db.refresh(color)
        return color

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Color code already exists or violates a database constraint.",
        )


def get_colors(db: Session, active_only: bool = False):
    query = select(Color)

    if active_only:
        query = query.where(Color.is_active.is_(True))

    return db.scalars(query.order_by(Color.id)).all()


def get_color(db: Session, color_id: int):
    color = db.get(Color, color_id)

    if not color:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Color not found.",
        )

    return color


def update_color(db: Session, color_id: int, data: ColorUpdate):
    color = get_color(db, color_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Color code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Color).where(
            Color.code == code,
            Color.id != color_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Color code already exists.",
        )

    color.code = code
    color.name = name

    try:
        db.commit()
        db.refresh(color)
        return color

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Color update violates a database constraint.",
        )


def update_color_status(
    db: Session,
    color_id: int,
    data: ColorStatusUpdate,
):
    color = get_color(db, color_id)

    color.is_active = data.is_active

    db.commit()
    db.refresh(color)

    return color
