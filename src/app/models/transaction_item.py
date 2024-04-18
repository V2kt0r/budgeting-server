from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from .mixins.purchase_category import PurchaseCategoryMixin

association_table_transaction_item_transaction = Table(
    "association_transaction_item_transaction",
    Base.metadata,
    Column(
        "transaction_item_id",
        Integer,
        ForeignKey("transaction_item.id"),
        primary_key=True,
    ),
    Column(
        "transaction_id",
        Integer,
        ForeignKey("transaction.id"),
        primary_key=True,
    ),
)


class TransactionItem(
    PurchaseCategoryMixin,
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
