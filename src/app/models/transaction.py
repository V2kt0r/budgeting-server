from enum import Enum

from sqlalchemy.orm import Mapped, Relationship, mapped_column, relationship

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from .mixins.misc import TimeMixin
from .mixins.purchase_category import PurchaseCategoryMixin
from .transaction_item import (
    TransactionItem,
    association_table_transaction_item_transaction,
)


class Currency(Enum):
    EUR = "EUR"
    USD = "USD"
    HUF = "HUF"


class Transaction(
    TimeMixin,
    PurchaseCategoryMixin,
    IDMixin,
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
    kw_only=True,
):
    amount: Mapped[float] = mapped_column(index=True)
    currency: Mapped[Currency] = mapped_column(index=True)
    name: Mapped[str | None] = mapped_column()
    description: Mapped[str | None] = mapped_column()

    transaction_items: Relationship[TransactionItem] = relationship(
        secondary=association_table_transaction_item_transaction
    )
