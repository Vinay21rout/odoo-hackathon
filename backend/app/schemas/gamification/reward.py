from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class RewardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    points_required: int = Field(100, ge=1)
    stock: int = Field(10, ge=0)

class RewardCreate(RewardBase):
    pass

class RewardUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    points_required: int | None = Field(None, ge=1)
    stock: int | None = Field(None, ge=0)

class RewardResponse(RewardBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class RewardRedeemRequest(BaseModel):
    user_id: UUID
    reward_id: UUID

class RewardRedemptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    reward_id: UUID
    redeemed_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
