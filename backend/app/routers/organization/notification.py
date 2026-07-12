from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.dependencies.database import get_db
from app.schemas.organization.notification import NotificationResponse
from app.services.organization.notification import notification_service
from app.services.common.response import success_response
from app.models.organization.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=None, status_code=status.HTTP_200_OK)
def read_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifications = notification_service.get_unread_for_user(db, current_user.id)
    data = [NotificationResponse.model_validate(n) for n in notifications]
    return success_response(data=data, message="Unread notifications retrieved successfully")

@router.put("/{id}/read", response_model=None, status_code=status.HTTP_200_OK)
def mark_notification_read(
    id: UUID,
    db: Session = Depends(get_db)
):
    n = notification_service.mark_as_read(db, id)
    data = NotificationResponse.model_validate(n) if n else None
    return success_response(data=data, message="Notification marked as read")
