from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class Tier(
    IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base, kw_only=True
):
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
