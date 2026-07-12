from sqlalchemy.orm import Session
from app.models.organization.notification import Notification
from app.services.common.crud import CRUDBase
from uuid import UUID

class CRUDNotification(CRUDBase[Notification]):
    def get_unread_for_user(self, db: Session, user_id: UUID) -> list[Notification]:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_active == True
        ).order_by(Notification.created_at.desc()).all()

    def mark_as_read(self, db: Session, notification_id: UUID) -> Notification:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.is_active == True
        ).first()
        if notification:
            notification.is_read = True
            db.add(notification)
            db.commit()
            db.refresh(notification)
        return notification

    def trigger_notification(self, db: Session, user_id: UUID, message: str, notification_type: str = "info") -> Notification:
        # Check if settings allow notifications
        from app.services.organization.settings import settings_service
        settings_obj = settings_service.get_active_settings(db)
        if settings_obj.in_app_notifications:
            notification = Notification(
                user_id=user_id,
                message=message,
                type=notification_type,
                is_read=False
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        return None

notification_service = CRUDNotification(Notification)
