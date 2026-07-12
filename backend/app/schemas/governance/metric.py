from datetime import datetime, date
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class GovernanceBase(BaseModel):
    metric_type: str = Field(..., min_length=1, max_length=50)
    value: float = Field(..., ge=0.0)
    status: str = Field("pending", min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=255)
    recorded_date: date

class GovernanceCreate(GovernanceBase):
    user_id: UUID

class GovernanceUpdate(BaseModel):
    metric_type: Optional[str] = Field(None, min_length=1, max_length=50)
    value: Optional[float] = Field(None, ge=0.0)
    status: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=255)
    recorded_date: Optional[date] = None

class GovernanceResponse(GovernanceBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
