from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=255)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=255)

class DepartmentResponse(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
