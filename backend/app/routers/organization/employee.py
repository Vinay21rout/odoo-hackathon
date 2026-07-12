from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.organization.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.organization.employee import employee_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.core.logger import logger
from app.core.constants import (
    MSG_EMP_RETRIEVED,
    MSG_EMP_NOT_FOUND,
    MSG_EMP_CREATED,
    MSG_EMP_UPDATED,
    MSG_EMP_DELETED,
)

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", status_code=status.HTTP_200_OK)
def read_employees(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving employees (page: {params.page}, limit: {params.limit})")
    query = employee_service.get_query(db)
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        EmployeeResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message=MSG_EMP_RETRIEVED)

@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_employee(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Retrieving employee {id}")
    db_obj = employee_service.get(db, id)
    if not db_obj:
        logger.warning(f"Employee {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_EMP_NOT_FOUND)
    data = EmployeeResponse.model_validate(db_obj)
    return success_response(data=data, message=MSG_EMP_RETRIEVED)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee(obj_in: EmployeeCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating employee with email: {obj_in.email}")
    db_obj = employee_service.create(db, obj_in=obj_in)
    data = EmployeeResponse.model_validate(db_obj)
    return success_response(data=data, message=MSG_EMP_CREATED)

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_employee(id: UUID, obj_in: EmployeeUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating employee {id}")
    db_obj = employee_service.get(db, id)
    if not db_obj:
        logger.warning(f"Employee {id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_EMP_NOT_FOUND)
    db_obj = employee_service.update(db, db_obj=db_obj, obj_in=obj_in)
    data = EmployeeResponse.model_validate(db_obj)
    return success_response(data=data, message=MSG_EMP_UPDATED)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_employee(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting employee {id}")
    db_obj = employee_service.get(db, id)
    if not db_obj:
        logger.warning(f"Employee {id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_EMP_NOT_FOUND)
    employee_service.remove(db, id=id)
    return success_response(message=MSG_EMP_DELETED)
