from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: UUID
    message: str = Field(..., min_length=1, max_length=255)
    type: str = Field("info", min_length=1, max_length=50)
    is_read: bool = False

class NotificationResponse(NotificationBase):
    id: UUID
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
