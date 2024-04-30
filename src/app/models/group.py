from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from .purchase_category import PurchaseCategory
from .tag import Tag

association_table_group_purchase_category = Table(
    "association_group_purchase_category",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id"), primary_key=True),
    Column(
        "purchase_category_id",
        ForeignKey("purchase_category.id"),
        primary_key=True,
    ),
)

association_table_group_tag = Table(
    "association_group_tag",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class Group(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    name: Mapped[str] = mapped_column(index=True)

    purchase_categories: Mapped[list[PurchaseCategory]] = relationship(
        secondary=association_table_group_purchase_category
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=association_table_group_tag
    )
