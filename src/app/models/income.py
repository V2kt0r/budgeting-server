from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class Income(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    is_net: Mapped[bool] = mapped_column(default=False)
    tax_rate: Mapped[float | None] = mapped_column(default=0.335)
    amount: Mapped[float] = mapped_column(index=True)
    name: Mapped[str] = mapped_column()
