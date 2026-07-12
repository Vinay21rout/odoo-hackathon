from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.organization.settings import SettingsUpdate, SettingsResponse
from app.services.organization.settings import settings_service
from app.services.common.response import success_response

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=None, status_code=status.HTTP_200_OK)
def read_settings(db: Session = Depends(get_db)):
    settings_obj = settings_service.get_active_settings(db)
    data = SettingsResponse.model_validate(settings_obj)
    return success_response(data=data, message="System configurations retrieved successfully")

@router.put("", response_model=None, status_code=status.HTTP_200_OK)
def update_settings(obj_in: SettingsUpdate, db: Session = Depends(get_db)):
    settings_obj = settings_service.update_settings(db, obj_in=obj_in)
    data = SettingsResponse.model_validate(settings_obj)
    return success_response(data=data, message="System configurations updated successfully")
