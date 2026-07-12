from datetime import datetime, date
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Challenge Schemas
class ChallengeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    points_reward: int = Field(10, ge=1)
    category: str = Field("environmental", min_length=1, max_length=50)
    start_date: date
    end_date: date

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    points_reward: Optional[int] = Field(None, ge=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ChallengeResponse(ChallengeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Badge Schemas
class BadgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    icon_url: Optional[str] = Field(None, max_length=255)
    points_target: int = Field(500, ge=0)

class BadgeCreate(BadgeBase):
    pass

class BadgeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    icon_url: Optional[str] = Field(None, max_length=255)
    points_target: Optional[int] = Field(None, ge=0)

class BadgeResponse(BadgeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Progress Tracking Schemas
class UserChallengeCreate(BaseModel):
    user_id: UUID
    challenge_id: UUID

class UserChallengeUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=20)

class UserChallengeResponse(BaseModel):
    id: UUID
    user_id: UUID
    challenge_id: UUID
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserBadgeCreate(BaseModel):
    user_id: UUID
    badge_id: UUID

class UserBadgeResponse(BaseModel):
    id: UUID
    user_id: UUID
    badge_id: UUID
    earned_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Leaderboard Entry
class LeaderboardEntry(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    total_points: int
