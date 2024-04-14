from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class TimeMixin:
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
        index=True,
        nullable=False,
    )


class DismissedMixin:
    dismissed: Mapped[bool] = mapped_column(
        index=True, default=False, nullable=False
    )
