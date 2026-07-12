from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.governance.metric import GovernanceCreate, GovernanceUpdate, GovernanceResponse
from app.services.governance.metric import governance_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.models.governance.metric import GovernanceRecord
from app.core.logger import logger

router = APIRouter(prefix="/governance", tags=["Governance"])

@router.get("", status_code=status.HTTP_200_OK)
def read_governance_records(
    metric_type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "recorded_date",
    sort_order: str = "desc",
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving governance records (type: '{metric_type}', status: '{status}', user: {user_id})")
    query = governance_service.get_query(db)
    
    # Filtering
    if metric_type:
        query = query.filter(GovernanceRecord.metric_type == metric_type)
    if status:
        query = query.filter(GovernanceRecord.status == status)
    if user_id:
        query = query.filter(GovernanceRecord.user_id == user_id)
        
    # Search
    if search:
        query = query.filter(GovernanceRecord.description.ilike(f"%{search}%"))
        
    # Sorting
    if sort_by and hasattr(GovernanceRecord, sort_by):
        col = getattr(GovernanceRecord, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(col.asc())
        else:
            query = query.order_by(col.desc())
    else:
        query = query.order_by(GovernanceRecord.recorded_date.desc())
        
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        GovernanceResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Governance records retrieved successfully")

@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_governance_record(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Retrieving governance record {id}")
    db_obj = governance_service.get(db, id)
    if not db_obj:
        logger.warning(f"Governance record {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Governance record not found")
    data = GovernanceResponse.model_validate(db_obj)
    return success_response(data=data, message="Governance record retrieved successfully")

@router.post("", status_code=status.HTTP_201_CREATED)
def create_governance_record(obj_in: GovernanceCreate, db: Session = Depends(get_db)):
    db_obj = governance_service.create(db, obj_in=obj_in)
    data = GovernanceResponse.model_validate(db_obj)
    return success_response(data=data, message="Governance record created successfully")

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_governance_record(id: UUID, obj_in: GovernanceUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating governance record {id}")
    db_obj = governance_service.get(db, id)
    if not db_obj:
        logger.warning(f"Governance record {id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Governance record not found")
    db_obj = governance_service.update(db, db_obj=db_obj, obj_in=obj_in)
    data = GovernanceResponse.model_validate(db_obj)
    return success_response(data=data, message="Governance record updated successfully")

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_governance_record(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting governance record {id}")
    db_obj = governance_service.get(db, id)
    if not db_obj:
        logger.warning(f"Governance record {id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Governance record not found")
    governance_service.remove(db, id=id)
    return success_response(message="Governance record deleted successfully")
