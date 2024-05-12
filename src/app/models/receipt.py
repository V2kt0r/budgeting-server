from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class ReceiptStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    PROCESSED = "processed"


class Receipt(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    url: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    status: Mapped[ReceiptStatus] = mapped_column(
        index=True, default=ReceiptStatus.PENDING
    )
