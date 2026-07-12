from datetime import date
from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import BaseModel

class Challenge(BaseModel):
    __tablename__ = "challenges"

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    points_reward: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False
    )
