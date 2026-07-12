from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.organization.department import Department
from app.schemas.organization.department import DepartmentCreate, DepartmentUpdate
from app.services.common.crud import CRUDBase
from app.core.logger import logger

class CRUDDepartment(CRUDBase[Department]):
    def check_unique_constraints(
        self, db: Session, *, name: str, code: str, exclude_id: Optional[Any] = None
    ) -> None:
        logger.info(f"Checking unique constraints for department (name: '{name}', code: '{code}')")
        
        # Check name
        query_name = db.query(Department).filter(
            Department.name == name,
            Department.is_active == True
        )
        if exclude_id:
            query_name = query_name.filter(Department.id != exclude_id)
        if query_name.first():
            logger.warning(f"Department name constraint violation: '{name}' already exists.")
            raise HTTPException(
                status_code=400,
                detail=f"Department with name '{name}' already exists."
            )

        # Check code
        query_code = db.query(Department).filter(
            Department.code == code,
            Department.is_active == True
        )
        if exclude_id:
            query_code = query_code.filter(Department.id != exclude_id)
        if query_code.first():
            logger.warning(f"Department code constraint violation: '{code}' already exists.")
            raise HTTPException(
                status_code=400,
                detail=f"Department with code '{code}' already exists."
            )

    def create(self, db: Session, *, obj_in: DepartmentCreate) -> Department:
        self.check_unique_constraints(db, name=obj_in.name, code=obj_in.code)
        logger.info(f"Creating department in DB: {obj_in.name}")
        return super().create(db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: Department, obj_in: DepartmentUpdate
    ) -> Department:
        name = obj_in.name if obj_in.name is not None else db_obj.name
        code = obj_in.code if obj_in.code is not None else db_obj.code
        self.check_unique_constraints(db, name=name, code=code, exclude_id=db_obj.id)
        logger.info(f"Updating department in DB: {db_obj.id}")
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

department_service = CRUDDepartment(Department)
