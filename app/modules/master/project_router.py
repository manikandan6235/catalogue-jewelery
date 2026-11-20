
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.modules.master.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)

from app.modules.master import project_service


router = APIRouter(
    prefix="/masters/projects",
    tags=["Project Master"]
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db)
):
    return project_service.create_project(db, data)


@router.get(
    "/",
    response_model=list[ProjectResponse]
)
def get_projects(
    db: Session = Depends(get_db)
):
    return project_service.get_projects(db)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    return project_service.get_project(db, project_id)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    return project_service.update_project(
        db, project_id, data
    )


@router.patch(
    "/{project_id}/deactivate",
    response_model=ProjectResponse
)
def deactivate_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    return project_service.deactivate_project(
        db, project_id
    )
