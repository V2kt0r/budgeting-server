import uuid as uuid_pkg

from sqlalchemy import Column, ForeignKey, Integer, String, Table
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

association_table_user_purchase_category = Table(
    "association_user_purchase_category",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column(
        "purchase_category_id",
        ForeignKey("purchase_category.id"),
        primary_key=True,
    ),
)

association_table_user_tag = Table(
    "association_user_tag",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class User(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    profile_image_url: Mapped[str | None] = mapped_column(String, default=None)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    tier_id: Mapped[int | None] = mapped_column(
        ForeignKey("tier.id"), index=True, default=None
    )
    tier_uuid: Mapped[uuid_pkg.UUID | None] = mapped_column(
        index=True, default=None
    )

    # purchase_categories: Mapped[list[PurchaseCategory]] = relationship(
    #     secondary=association_table_user_purchase_category, default_factory=list
    # )
    # tags: Mapped[list[Tag]] = relationship(
    #     secondary=association_table_user_tag, default_factory=list
    # )
