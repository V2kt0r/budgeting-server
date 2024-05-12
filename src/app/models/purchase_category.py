from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class PurchaseCategory(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    category_name: Mapped[str] = mapped_column(index=True)
    category_description: Mapped[str | None] = mapped_column()
