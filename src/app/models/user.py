import uuid as uuid_pkg

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.models.mixins import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
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
