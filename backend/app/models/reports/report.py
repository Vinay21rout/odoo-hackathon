from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User

class SavedReport(BaseModel):
    __tablename__ = "saved_reports"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    report_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )  # "esg_summary", "carbon_footprint", "social_impact"
    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    user: Mapped["User"] = relationship()
