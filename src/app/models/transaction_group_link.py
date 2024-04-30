import uuid as uuid_pkg

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class TransactionGroupLink(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transaction.id"), index=True, unique=True
    )
    transaction_uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        index=True, unique=True
    )
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), index=True)
    group_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True
    )
    created_by_user_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
