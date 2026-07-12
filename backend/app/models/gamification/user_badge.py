from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User
    from app.models.gamification.badge import Badge

class UserBadge(BaseModel):
    __tablename__ = "user_badges"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    badge_id: Mapped[UUID] = mapped_column(
        ForeignKey("badges.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship()
    badge: Mapped["Badge"] = relationship()
