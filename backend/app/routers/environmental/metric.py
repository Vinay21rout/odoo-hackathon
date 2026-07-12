from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.environmental.metric import EnvironmentalCreate, EnvironmentalUpdate, EnvironmentalResponse
from app.services.environmental.metric import environmental_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.models.environmental.metric import EnvironmentalRecord
from app.core.logger import logger

router = APIRouter(prefix="/environmental", tags=["Environmental"])

@router.get("", status_code=status.HTTP_200_OK)
def read_environmental_records(
    metric_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "recorded_date",
    sort_order: str = "desc",
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving environmental records (type: '{metric_type}', user: {user_id}, search: '{search}')")
    query = environmental_service.get_query(db)
    
    # Filtering
    if metric_type:
        query = query.filter(EnvironmentalRecord.metric_type == metric_type)
    if user_id:
        query = query.filter(EnvironmentalRecord.user_id == user_id)
        
    # Search
    if search:
        query = query.filter(EnvironmentalRecord.description.ilike(f"%{search}%"))
        
    # Sorting
    if sort_by and hasattr(EnvironmentalRecord, sort_by):
        col = getattr(EnvironmentalRecord, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(col.asc())
        else:
            query = query.order_by(col.desc())
    else:
        query = query.order_by(EnvironmentalRecord.recorded_date.desc())
        
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        EnvironmentalResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Environmental records retrieved successfully")

@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_environmental_record(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Retrieving environmental record {id}")
    db_obj = environmental_service.get(db, id)
    if not db_obj:
        logger.warning(f"Environmental record {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environmental record not found")
    data = EnvironmentalResponse.model_validate(db_obj)
    return success_response(data=data, message="Environmental record retrieved successfully")

@router.post("", status_code=status.HTTP_201_CREATED)
def create_environmental_record(obj_in: EnvironmentalCreate, db: Session = Depends(get_db)):
    db_obj = environmental_service.create(db, obj_in=obj_in)
    data = EnvironmentalResponse.model_validate(db_obj)
    return success_response(data=data, message="Environmental record created successfully")

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_environmental_record(id: UUID, obj_in: EnvironmentalUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating environmental record {id}")
    db_obj = environmental_service.get(db, id)
    if not db_obj:
        logger.warning(f"Environmental record {id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environmental record not found")
    db_obj = environmental_service.update(db, db_obj=db_obj, obj_in=obj_in)
    data = EnvironmentalResponse.model_validate(db_obj)
    return success_response(data=data, message="Environmental record updated successfully")

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_environmental_record(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting environmental record {id}")
    db_obj = environmental_service.get(db, id)
    if not db_obj:
        logger.warning(f"Environmental record {id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environmental record not found")
    environmental_service.remove(db, id=id)
    return success_response(message="Environmental record deleted successfully")
