
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Gender
from app.modules.master.gender_schema import (
    GenderCreate,
    GenderUpdate,
    GenderStatusUpdate,
)


def create_gender(db: Session, data: GenderCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gender code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Gender).where(Gender.code == code)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gender code already exists.",
        )

    gender = Gender(
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(gender)
        db.commit()
        db.refresh(gender)
        return gender

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gender code already exists or violates a database constraint.",
        )


def get_genders(db: Session, active_only: bool = False):
    query = select(Gender)

    if active_only:
        query = query.where(Gender.is_active.is_(True))

    return db.scalars(query.order_by(Gender.id)).all()


def get_gender(db: Session, gender_id: int):
    gender = db.get(Gender, gender_id)

    if not gender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gender not found.",
        )

    return gender


def update_gender(db: Session, gender_id: int, data: GenderUpdate):
    gender = get_gender(db, gender_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gender code and name cannot be empty.",
        )

    existing = db.scalar(
        select(Gender).where(
            Gender.code == code,
            Gender.id != gender_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gender code already exists.",
        )

    gender.code = code
    gender.name = name

    try:
        db.commit()
        db.refresh(gender)
        return gender

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gender update violates a database constraint.",
        )


def update_gender_status(
    db: Session,
    gender_id: int,
    data: GenderStatusUpdate,
):
    gender = get_gender(db, gender_id)

    gender.is_active = data.is_active

    db.commit()
    db.refresh(gender)

    return gender
