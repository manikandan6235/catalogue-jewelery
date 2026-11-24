
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Style
from app.modules.master.style_schema import (
    StyleCreate,
    StyleUpdate,
    StyleStatusUpdate,
)


def create_style(db: Session, data: StyleCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Style code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Style).where(Style.code == code)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Style code already exists.",
        )

    style = Style(
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(style)
        db.commit()
        db.refresh(style)
        return style

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Style code already exists or violates a database constraint.",
        )


def get_styles(db: Session, active_only: bool = False):
    query = select(Style)

    if active_only:
        query = query.where(Style.is_active.is_(True))

    return db.scalars(query.order_by(Style.id)).all()


def get_style(db: Session, style_id: int):
    style = db.get(Style, style_id)

    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style not found.",
        )

    return style


def update_style(db: Session, style_id: int, data: StyleUpdate):
    style = get_style(db, style_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Style code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Style).where(
            Style.code == code,
            Style.id != style_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Style code already exists.",
        )

    style.code = code
    style.name = name

    try:
        db.commit()
        db.refresh(style)
        return style

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Style update violates a database constraint.",
        )


def update_style_status(
    db: Session,
    style_id: int,
    data: StyleStatusUpdate,
):
    style = get_style(db, style_id)

    style.is_active = data.is_active

    db.commit()
    db.refresh(style)

    return style
