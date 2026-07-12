from uuid import UUID
from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User

class EnvironmentalRecord(BaseModel):
    __tablename__ = "environmental_records"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    metric_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )  # "carbon", "energy", "water", "waste"
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # "kgCO2e", "kWh", "m3", "kg"
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
