from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from .mixins.purchase_category import PurchaseCategoryMixin
from .tag import Tag

association_table_transaction_item_tag = Table(
    "association_transaction_item_tag",
    Base.metadata,
    Column(
        "transaction_item_id",
        Integer,
        ForeignKey("transaction_item.id"),
        primary_key=True,
    ),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
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

    tags: Mapped[list[Tag]] = relationship(
        secondary=association_table_transaction_item_tag
    )
