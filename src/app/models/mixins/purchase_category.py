import uuid as uuid_pkg

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class PurchaseCategoryMixin:
    purchase_category_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_category.id"), index=True
    )
    purchase_category_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
