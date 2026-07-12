from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.auth.role import Role
    from app.models.organization.department import Department


class User(BaseModel):
    __tablename__ = "users"

    firebase_uid: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        index=True
    )

    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        index=True
    )

    role: Mapped["Role"] = relationship(back_populates="users")

    department: Mapped["Department"] = relationship(back_populates="users")
