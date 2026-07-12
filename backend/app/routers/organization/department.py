from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.organization.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.services.organization.department import department_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.core.logger import logger
from app.core.constants import (
    MSG_DEPT_RETRIEVED,
    MSG_DEPT_NOT_FOUND,
    MSG_DEPT_CREATED,
    MSG_DEPT_UPDATED,
    MSG_DEPT_DELETED,
)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("", status_code=status.HTTP_200_OK)
def read_departments(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving departments (page: {params.page}, limit: {params.limit})")
    query = department_service.get_query(db)
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        DepartmentResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message=MSG_DEPT_RETRIEVED)

@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_department(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Retrieving department {id}")
    db_obj = department_service.get(db, id)
    if not db_obj:
        logger.warning(f"Department {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_DEPT_NOT_FOUND)
    data = DepartmentResponse.model_validate(db_obj)
    return success_response(data=data, message=MSG_DEPT_RETRIEVED)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_department(obj_in: DepartmentCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating department with name: {obj_in.name}")
    db_obj = department_service.create(db, obj_in=obj_in)
    data = DepartmentResponse.model_validate(db_obj)
    return success_response(data=data, message=MSG_DEPT_CREATED)

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_department(id: UUID, obj_in: DepartmentUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating department {id}")
    db_obj = department_service.get(db, id)
    if not db_obj:
        logger.warning(f"Department {id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_DEPT_NOT_FOUND)
    db_obj = department_service.update(db, db_obj=db_obj, obj_in=obj_in)
    data = DepartmentResponse.model_validate(db_obj)
    return success_response(data=data, message=MSG_DEPT_UPDATED)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_department(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting department {id}")
    db_obj = department_service.get(db, id)
    if not db_obj:
        logger.warning(f"Department {id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_DEPT_NOT_FOUND)
    department_service.remove(db, id=id)
    return success_response(message=MSG_DEPT_DELETED)
