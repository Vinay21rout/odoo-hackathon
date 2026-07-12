from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User

class Reward(BaseModel):
    __tablename__ = "rewards"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    points_required: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

class RewardRedemption(BaseModel):
    __tablename__ = "reward_redemptions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    reward_id: Mapped[UUID] = mapped_column(
        ForeignKey("rewards.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship()
    reward: Mapped["Reward"] = relationship()
