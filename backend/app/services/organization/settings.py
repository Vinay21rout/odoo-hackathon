from sqlalchemy.orm import Session
from app.models.organization.settings import SystemSettings
from app.schemas.organization.settings import SettingsUpdate
from app.services.common.crud import CRUDBase

class CRUDSettings(CRUDBase[SystemSettings]):
    def get_active_settings(self, db: Session) -> SystemSettings:
        settings_obj = db.query(SystemSettings).filter(SystemSettings.is_active == True).first()
        if not settings_obj:
            # Seed default settings if they don't exist
            settings_obj = SystemSettings(
                auto_emission_calculation=True,
                evidence_requirement=False,
                badge_auto_award=True,
                email_notifications=True,
                in_app_notifications=True
            )
            db.add(settings_obj)
            db.commit()
            db.refresh(settings_obj)
        return settings_obj

    def update_settings(self, db: Session, *, obj_in: SettingsUpdate) -> SystemSettings:
        settings_obj = self.get_active_settings(db)
        return self.update(db, db_obj=settings_obj, obj_in=obj_in)

settings_service = CRUDSettings(SystemSettings)
