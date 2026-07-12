from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.social.metric import SocialCreate, SocialUpdate, SocialResponse
from app.services.social.metric import social_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.core.logger import logger

router = APIRouter(prefix="/social", tags=["Social"])

@router.get("", status_code=status.HTTP_200_OK)
def read_social_records(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving social records (page: {params.page}, limit: {params.limit})")
    query = social_service.get_query(db)
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        SocialResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Social records retrieved successfully")

@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_social_record(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Retrieving social record {id}")
    db_obj = social_service.get(db, id)
    if not db_obj:
        logger.warning(f"Social record {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social record not found")
    data = SocialResponse.model_validate(db_obj)
    return success_response(data=data, message="Social record retrieved successfully")

@router.post("", status_code=status.HTTP_201_CREATED)
def create_social_record(obj_in: SocialCreate, db: Session = Depends(get_db)):
    db_obj = social_service.create(db, obj_in=obj_in)
    data = SocialResponse.model_validate(db_obj)
    return success_response(data=data, message="Social record created successfully")

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_social_record(id: UUID, obj_in: SocialUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating social record {id}")
    db_obj = social_service.get(db, id)
    if not db_obj:
        logger.warning(f"Social record {id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social record not found")
    db_obj = social_service.update(db, db_obj=db_obj, obj_in=obj_in)
    data = SocialResponse.model_validate(db_obj)
    return success_response(data=data, message="Social record updated successfully")

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_social_record(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting social record {id}")
    db_obj = social_service.get(db, id)
    if not db_obj:
        logger.warning(f"Social record {id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social record not found")
    social_service.remove(db, id=id)
    return success_response(message="Social record deleted successfully")
