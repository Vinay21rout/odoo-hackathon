from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class SettingsBase(BaseModel):
    auto_emission_calculation: bool
    evidence_requirement: bool
    badge_auto_award: bool
    email_notifications: bool
    in_app_notifications: bool

class SettingsUpdate(BaseModel):
    auto_emission_calculation: bool | None = None
    evidence_requirement: bool | None = None
    badge_auto_award: bool | None = None
    email_notifications: bool | None = None
    in_app_notifications: bool | None = None

class SettingsResponse(SettingsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
