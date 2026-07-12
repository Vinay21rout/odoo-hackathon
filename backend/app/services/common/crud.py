from typing import Any, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from app.models.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.is_active == True
        ).first()

    def get_query(self, db: Session) -> Any:
        return db.query(self.model).filter(self.model.is_active == True)

    def get_multi(
        self, db: Session, *, page: int = 1, limit: int = 10
    ) -> List[ModelType]:
        offset = (page - 1) * limit
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: Any) -> ModelType:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Any
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            db_obj.is_active = False  # Soft delete
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
