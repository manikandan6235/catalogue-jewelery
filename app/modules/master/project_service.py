
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.modules.master.master import Project
from app.modules.master.project_schema import (
    ProjectCreate,
    ProjectUpdate
)


def create_project(db: Session, data: ProjectCreate):

    existing = db.scalar(
        select(Project).where(Project.code == data.code)
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Project code already exists"
        )

    project = Project(**data.model_dump())

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise


def get_projects(db: Session):

    return db.scalars(
        select(Project).order_by(Project.id)
    ).all()


def get_project(db: Session, project_id: int):

    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


def update_project(
    db: Session,
    project_id: int,
    data: ProjectUpdate
):

    project = get_project(db, project_id)

    update_data = data.model_dump(exclude_unset=True)

    if update_data.get("code") is not None:

        existing = db.scalar(
            select(Project).where(
                Project.code == update_data["code"],
                Project.id != project_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Project code already exists"
            )

    for key, value in update_data.items():
        setattr(project, key, value)

    try:
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise


def deactivate_project(db: Session, project_id: int):

    project = get_project(db, project_id)

    project.is_active = False

    try:
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise
