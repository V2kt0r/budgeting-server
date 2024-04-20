from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, Table
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
from .receipt import Receipt
from .transaction_item import TransactionItem

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

association_table_transaction_receipt = Table(
    "association_transaction_receipt",
    Base.metadata,
    Column(
        "transaction_id",
        Integer,
        ForeignKey("transaction.id"),
        primary_key=True,
    ),
    Column("receipt_id", Integer, ForeignKey("receipt.id"), primary_key=True),
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
    receipts: Relationship[Receipt] = relationship(
        secondary=association_table_transaction_receipt
    )
