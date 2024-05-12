import uuid as uuid_pkg

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class TagMixin:
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"), index=True)
    tag_uuid: Mapped[uuid_pkg.UUID] = mapped_column(index=True)


class TagOptionalMixin:
    tag_id: Mapped[int | None] = mapped_column(ForeignKey("tag.id"), index=True)
    tag_uuid: Mapped[uuid_pkg.UUID | None] = mapped_column(index=True)
