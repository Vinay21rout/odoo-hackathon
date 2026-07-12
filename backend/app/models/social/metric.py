from uuid import UUID
from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User

class SocialRecord(BaseModel):
    __tablename__ = "social_records"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    metric_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )  # "training_hours", "health_safety_incidents", "diversity_ratio", "community_hours"
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    recorded_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        index=True,
        nullable=False
    )

    user: Mapped["User"] = relationship()
