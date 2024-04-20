from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from .mixins.purchase_category import PurchaseCategoryMixin
from .mixins.tag import TagOptionalMixin


class TransactionItem(
    PurchaseCategoryMixin,
    TagOptionalMixin,
    IDMixin,
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
    kw_only=True,
):
    amount: Mapped[float] = mapped_column(index=True)
    name: Mapped[str | None] = mapped_column()
    description: Mapped[str | None] = mapped_column()
