from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.reports.report import ReportCreate, ReportUpdate, ReportResponse
from app.services.reports.report_service import report_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.models.reports.report import SavedReport
from app.core.logger import logger

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/dynamic", status_code=status.HTTP_200_OK)
def get_dynamic_esg_report(db: Session = Depends(get_db)):
    logger.info("Requesting dynamically aggregated ESG report")
    report_data = report_service.generate_dynamic_esg_report(db)
    return success_response(data=report_data, message="Dynamic ESG report compiled successfully")

@router.get("", status_code=status.HTTP_200_OK)
def read_saved_reports(
    report_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: str = "desc",
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving saved reports (type: '{report_type}', user: {user_id}, search: '{search}')")
    query = report_service.get_query(db)
    
    # Filtering
    if report_type:
        query = query.filter(SavedReport.report_type == report_type)
    if user_id:
        query = query.filter(SavedReport.user_id == user_id)
        
    # Search
    if search:
        query = query.filter(SavedReport.title.ilike(f"%{search}%"))
        
    # Sorting
    if sort_by and hasattr(SavedReport, sort_by):
        col = getattr(SavedReport, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(col.asc())
        else:
            query = query.order_by(col.desc())
    else:
        query = query.order_by(SavedReport.created_at.desc())
        
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        ReportResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Saved reports retrieved successfully")

@router.post("", status_code=status.HTTP_201_CREATED)
def save_report(obj_in: ReportCreate, db: Session = Depends(get_db)):
    db_obj = report_service.create(db, obj_in=obj_in)
    data = ReportResponse.model_validate(db_obj)
    return success_response(data=data, message="Report saved successfully")

@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_saved_report(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Retrieving saved report {id}")
    db_obj = report_service.get(db, id)
    if not db_obj:
        logger.warning(f"Saved report {id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved report not found")
    data = ReportResponse.model_validate(db_obj)
    return success_response(data=data, message="Saved report retrieved successfully")

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_saved_report(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting saved report {id}")
    db_obj = report_service.get(db, id)
    if not db_obj:
        logger.warning(f"Saved report {id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved report not found")
    report_service.remove(db, id=id)
    return success_response(message="Saved report deleted successfully")
