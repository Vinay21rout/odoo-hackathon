from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import BaseModel

class Badge(BaseModel):
    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    icon_url: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    points_target: Mapped[int] = mapped_column(
        default=500,
        nullable=False
    )
