import uuid as uuid_pkg

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base
from ...core.models.mixins import TimestampMixin


class GroupPurchaseCategory(TimestampMixin, Base, kw_only=True):
    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.id"), index=True, primary_key=True
    )
    group_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    purchase_category_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_category.id"), index=True, primary_key=True
    )
    purchase_category_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
