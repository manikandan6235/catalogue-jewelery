
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Category, Subcategory
from app.modules.master.subcategory_Schema import (
    SubcategoryCreate,
    SubcategoryUpdate,
    SubcategoryStatusUpdate,
)


def create_subcategory(db: Session, data: SubcategoryCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory code and name cannot be empty.",
        )

    # Validate parent category
    category = db.scalar(
        select(Category).where(Category.id == data.category_id)
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    if not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a subcategory under an inactive category.",
        )

    # Check duplicate code within the same category
    existing = db.scalar(
        select(Subcategory).where(
            Subcategory.category_id == data.category_id,
            Subcategory.code == code,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This subcategory code already exists under this category.",
        )

    subcategory = Subcategory(
        category_id=data.category_id,
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(subcategory)
        db.commit()
        db.refresh(subcategory)
        return subcategory

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subcategory already exists or violates a database constraint.",
        )


def get_subcategories(
    db: Session,
    category_id: int | None = None,
    active_only: bool = False,
):
    query = select(Subcategory)

    if category_id is not None:
        query = query.where(Subcategory.category_id == category_id)

    if active_only:
        query = query.where(Subcategory.is_active.is_(True))

    query = query.order_by(Subcategory.id)

    return db.scalars(query).all()


def get_subcategory(db: Session, subcategory_id: int):
    subcategory = db.get(Subcategory, subcategory_id)

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found.",
        )

    return subcategory


def update_subcategory(
    db: Session,
    subcategory_id: int,
    data: SubcategoryUpdate,
):
    subcategory = get_subcategory(db, subcategory_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory code and name cannot be empty.",
        )

    # Check duplicate code under the same parent category
    existing = db.scalar(
        select(Subcategory).where(
            Subcategory.category_id == subcategory.category_id,
            Subcategory.code == code,
            Subcategory.id != subcategory_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This subcategory code already exists under this category.",
        )

    subcategory.code = code
    subcategory.name = name

    try:
        db.commit()
        db.refresh(subcategory)
        return subcategory

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subcategory update violates a database constraint.",
        )


def update_subcategory_status(
    db: Session,
    subcategory_id: int,
    data: SubcategoryStatusUpdate,
):
    subcategory = get_subcategory(db, subcategory_id)

    subcategory.is_active = data.is_active

    db.commit()
    db.refresh(subcategory)

    return subcategory
