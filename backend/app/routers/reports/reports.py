from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.reports.report import ReportCreate, ReportUpdate, ReportResponse
from app.services.reports.report_service import report_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.core.logger import logger

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/dynamic", status_code=status.HTTP_200_OK)
def get_dynamic_esg_report(db: Session = Depends(get_db)):
    logger.info("Requesting dynamically aggregated ESG report")
    report_data = report_service.generate_dynamic_esg_report(db)
    return success_response(data=report_data, message="Dynamic ESG report compiled successfully")

@router.get("", status_code=status.HTTP_200_OK)
def read_saved_reports(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving saved reports (page: {params.page}, limit: {params.limit})")
    query = report_service.get_query(db)
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
