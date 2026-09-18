import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base
from app.models.role import role_permissions

if TYPE_CHECKING:
    from app.models.role import Role


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("resource", "action", name="uq_permissions_resource_action"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
    )
