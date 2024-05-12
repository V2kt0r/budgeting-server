import uuid as uuid_pkg

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base
from ...core.models.mixins import TimestampMixin


class TransactionReceipt(TimestampMixin, Base, kw_only=True):
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transaction.id"), index=True, primary_key=True
    )
    transaction_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    receipt_id: Mapped[int] = mapped_column(
        ForeignKey("receipt.id"), index=True, primary_key=True
    )
    receipt_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
