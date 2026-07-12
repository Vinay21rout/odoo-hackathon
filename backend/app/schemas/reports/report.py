from datetime import datetime
from uuid import UUID
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class ReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    report_type: str = Field(..., min_length=1, max_length=50)
    content: Dict[str, Any]

class ReportCreate(ReportBase):
    user_id: UUID

class ReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    report_type: Optional[str] = Field(None, min_length=1, max_length=50)
    content: Optional[Dict[str, Any]] = None

class ReportResponse(ReportBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
