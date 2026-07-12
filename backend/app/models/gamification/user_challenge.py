from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User
    from app.models.gamification.challenge import Challenge

class UserChallenge(BaseModel):
    __tablename__ = "user_challenges"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    challenge_id: Mapped[UUID] = mapped_column(
        ForeignKey("challenges.id"),
        index=True,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        index=True,
        nullable=False
    )  # "in_progress", "completed"
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )

    user: Mapped["User"] = relationship()
    challenge: Mapped["Challenge"] = relationship()
