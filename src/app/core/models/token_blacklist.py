from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.database import Base
from ..models.mixins import IDMixin, SoftDeleteMixin, TimestampMixin


class TokenBlacklist(
    IDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    token: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
