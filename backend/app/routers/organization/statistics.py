from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services.organization.organization_service import organization_service
from app.services.common.response import success_response
from app.core.logger import logger
from app.core.constants import MSG_STATS_RETRIEVED

router = APIRouter(prefix="/organization", tags=["Organization"])

@router.get("/stats")
def get_org_stats(db: Session = Depends(get_db)):
    logger.info("Retrieving organization statistics")
    stats_data = organization_service.get_organization_stats(db)
    return success_response(
        data=stats_data,
        message=MSG_STATS_RETRIEVED
    )
