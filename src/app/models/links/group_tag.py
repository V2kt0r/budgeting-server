import uuid as uuid_pkg

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base
from ...core.models.mixins import TimestampMixin


class GroupTag(TimestampMixin, Base, kw_only=True):
    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.id"), index=True, primary_key=True
    )
    group_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tag.id"), index=True, primary_key=True
    )
    tag_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)
