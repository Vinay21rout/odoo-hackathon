from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    role_id: UUID
    department_id: UUID

class EmployeeCreate(EmployeeBase):
    firebase_uid: str = Field(..., min_length=1, max_length=255)

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=255)
    role_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

class EmployeeResponse(EmployeeBase):
    id: UUID
    firebase_uid: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
