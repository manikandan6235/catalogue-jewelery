
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.master.master import Collection, Subcollection
from app.modules.master.subcollection_schema import (
    SubcollectionCreate,
    SubcollectionUpdate,
    SubcollectionStatusUpdate,
)


def create_subcollection(db: Session, data: SubcollectionCreate):
    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcollection code and name cannot be empty.",
        )

    # Validate parent collection
    collection = db.scalar(
        select(Collection).where(Collection.id == data.collection_id)
    )

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    if not collection.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a subcollection under an inactive collection.",
        )

    # Check duplicate code within the same collection
    existing = db.scalar(
        select(Subcollection).where(
            Subcollection.collection_id == data.collection_id,
            Subcollection.code == code,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This subcollection code already exists under this collection.",
        )

    subcollection = Subcollection(
        collection_id=data.collection_id,
        code=code,
        name=name,
        is_active=data.is_active,
    )

    try:
        db.add(subcollection)
        db.commit()
        db.refresh(subcollection)
        return subcollection

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subcollection already exists or violates a database constraint.",
        )


def get_subcollections(
    db: Session,
    collection_id: int | None = None,
    active_only: bool = False,
):
    query = select(Subcollection)

    if collection_id is not None:
        query = query.where(Subcollection.collection_id == collection_id)

    if active_only:
        query = query.where(Subcollection.is_active.is_(True))

    query = query.order_by(Subcollection.id)

    return db.scalars(query).all()


def get_subcollection(db: Session, subcollection_id: int):
    subcollection = db.get(Subcollection, subcollection_id)

    if not subcollection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcollection not found.",
        )

    return subcollection


def update_subcollection(
    db: Session,
    subcollection_id: int,
    data: SubcollectionUpdate,
):
    subcollection = get_subcollection(db, subcollection_id)

    code = data.code.strip().upper()
    name = data.name.strip()

    if not code or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcollection code and name cannot be empty.",
        )

    # Check duplicate code under the same parent collection
    existing = db.scalar(
        select(Subcollection).where(
            Subcollection.collection_id == subcollection.collection_id,
            Subcollection.code == code,
            Subcollection.id != subcollection_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This subcollection code already exists under this collection.",
        )

    subcollection.code = code
    subcollection.name = name

    try:
        db.commit()
        db.refresh(subcollection)
        return subcollection

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subcollection update violates a database constraint.",
        )


def update_subcollection_status(
    db: Session,
    subcollection_id: int,
    data: SubcollectionStatusUpdate,
):
    subcollection = get_subcollection(db, subcollection_id)

    subcollection.is_active = data.is_active

    db.commit()
    db.refresh(subcollection)

    return subcollection
