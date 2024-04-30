import uuid as uuid_pkg
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base
from ...core.models.mixins import IDMixin, TimestampMixin, UUIDMixin


class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"


class UserGroupLink(IDMixin, UUIDMixin, TimestampMixin, Base, kw_only=True):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    user_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), index=True)
    group_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    user_role: Mapped[UserRole] = mapped_column(
        index=True, default=UserRole.MEMBER
    )
