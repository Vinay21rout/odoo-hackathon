from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.organization.user import User
from app.models.auth.role import Role
from app.models.organization.department import Department
from app.schemas.organization.employee import EmployeeCreate, EmployeeUpdate
from app.services.common.crud import CRUDBase
from app.core.logger import logger

class CRUDEmployee(CRUDBase[User]):
    def check_relations_and_uniqueness(
        self,
        db: Session,
        *,
        email: str,
        role_id: Any,
        department_id: Any,
        firebase_uid: Optional[str] = None,
        exclude_id: Optional[Any] = None
    ) -> None:
        logger.info(f"Validating relations and uniqueness for employee (email: '{email}')")
        
        # Validate Role exists and is active
        role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
        if not role:
            logger.warning(f"Role ID {role_id} validation failed.")
            raise HTTPException(
                status_code=400,
                detail=f"Role with ID '{role_id}' does not exist or is inactive."
            )

        # Validate Department exists and is active
        dept = db.query(Department).filter(
            Department.id == department_id,
            Department.is_active == True
        ).first()
        if not dept:
            logger.warning(f"Department ID {department_id} validation failed.")
            raise HTTPException(
                status_code=400,
                detail=f"Department with ID '{department_id}' does not exist or is inactive."
            )

        # Validate unique email
        query_email = db.query(User).filter(User.email == email, User.is_active == True)
        if exclude_id:
            query_email = query_email.filter(User.id != exclude_id)
        if query_email.first():
            logger.warning(f"Email uniqueness check failed: '{email}' already exists.")
            raise HTTPException(
                status_code=400,
                detail=f"Employee with email '{email}' already exists."
            )

        # Validate unique firebase_uid
        if firebase_uid:
            query_fb = db.query(User).filter(
                User.firebase_uid == firebase_uid,
                User.is_active == True
            )
            if exclude_id:
                query_fb = query_fb.filter(User.id != exclude_id)
            if query_fb.first():
                logger.warning(f"Firebase UID uniqueness check failed: '{firebase_uid}' already exists.")
                raise HTTPException(
                    status_code=400,
                    detail=f"Employee with Firebase UID '{firebase_uid}' already exists."
                )

    def create(self, db: Session, *, obj_in: EmployeeCreate) -> User:
        self.check_relations_and_uniqueness(
            db,
            email=obj_in.email,
            role_id=obj_in.role_id,
            department_id=obj_in.department_id,
            firebase_uid=obj_in.firebase_uid
        )
        logger.info(f"Creating employee in DB: {obj_in.email}")
        return super().create(db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: User, obj_in: EmployeeUpdate
    ) -> User:
        email = obj_in.email if obj_in.email is not None else db_obj.email
        role_id = obj_in.role_id if obj_in.role_id is not None else db_obj.role_id
        department_id = (
            obj_in.department_id if obj_in.department_id is not None else db_obj.department_id
        )
        self.check_relations_and_uniqueness(
            db,
            email=email,
            role_id=role_id,
            department_id=department_id,
            exclude_id=db_obj.id
        )
        logger.info(f"Updating employee in DB: {db_obj.id}")
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

employee_service = CRUDEmployee(User)
