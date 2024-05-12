import uuid as uuid_pkg
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base
from ...core.models.mixins import TimestampMixin


class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"


class GroupUser(TimestampMixin, Base, kw_only=True):
    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.id"), index=True, primary_key=True
    )
    group_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True, primary_key=True
    )
    user_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    user_role: Mapped[UserRole] = mapped_column(
        index=True, default=UserRole.MEMBER
    )
