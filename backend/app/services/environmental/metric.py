from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.environmental.metric import EnvironmentalRecord
from app.models.organization.user import User
from app.schemas.environmental.metric import EnvironmentalCreate, EnvironmentalUpdate
from app.services.common.crud import CRUDBase
from app.core.logger import logger

class CRUDEnvironmental(CRUDBase[EnvironmentalRecord]):
    def create(self, db: Session, *, obj_in: EnvironmentalCreate) -> EnvironmentalRecord:
        user = db.query(User).filter(User.id == obj_in.user_id, User.is_active == True).first()
        if not user:
            logger.warning(f"User ID {obj_in.user_id} not found when creating environmental record.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID '{obj_in.user_id}' does not exist or is inactive."
            )
        logger.info(f"Creating environmental record for user {obj_in.user_id} of type '{obj_in.metric_type}'")
        return super().create(db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: EnvironmentalRecord, obj_in: EnvironmentalUpdate
    ) -> EnvironmentalRecord:
        logger.info(f"Updating environmental record {db_obj.id}")
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

environmental_service = CRUDEnvironmental(EnvironmentalRecord)
