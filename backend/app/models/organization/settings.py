from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import BaseModel

class SystemSettings(BaseModel):
    __tablename__ = "system_settings"

    auto_emission_calculation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    evidence_requirement: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    badge_auto_award: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    in_app_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
