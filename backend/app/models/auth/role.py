from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.organization.user import User


class Role(BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    description: Mapped[str] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")