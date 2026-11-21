
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.modules.master.master import Category


def get_categories(db: Session, active_only: bool = False):
    query = db.query(Category)

    if active_only:
        query = query.filter(Category.is_active.is_(True))

    return query.order_by(Category.name.asc()).all()


def get_category_by_id(db: Session, category_id: int):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


def create_category(db: Session, data):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=422,
            detail="Category code and name cannot be empty"
        )

    existing = (
        db.query(Category)
        .filter(Category.code == code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Category code already exists"
        )

    category = Category(
        code=code,
        name=name,
        is_active=data.is_active
    )

    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category code already exists"
        )


def update_category(db: Session, category_id: int, data):
    category = get_category_by_id(db, category_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=422,
            detail="Category code and name cannot be empty"
        )

    duplicate = (
        db.query(Category)
        .filter(
            Category.code == code,
            Category.id != category_id
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Category code already exists"
        )

    category.code = code
    category.name = name

    try:
        db.commit()
        db.refresh(category)
        return category

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category code already exists"
        )


def update_category_status(
    db: Session,
    category_id: int,
    is_active: bool
):
    category = get_category_by_id(db, category_id)

    category.is_active = is_active

    db.commit()
    db.refresh(category)

    return category
