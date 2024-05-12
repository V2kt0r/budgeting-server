import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)


class TierBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=30,
            examples=["free", "mobile", "web", "admin"],
            description="Tier name must be unique and between 2 and 30 characters long.",
        ),
    ]


class TierBaseExternal(UUIDSchema, TierBase):
    pass


class TierBaseInternal(IDSchema, TierBase):
    pass


class Tier(
    TimestampSchema,
    PersistentDeletionSchema,
    TierBaseExternal,
    TierBaseInternal,
):
    pass


class TierRead(TimestampSchema, TierBaseExternal):
    pass


class TierCreate(TierBase):
    model_config = ConfigDict(extra="forbid")


class TierCreateInternal(TierCreate):
    pass


class TierUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str | None,
        Field(
            min_length=2,
            max_length=30,
            examples=["free", "mobile", "web", "admin"],
            description="Tier name must be unique and between 2 and 30 characters long.",
        ),
    ]


class TierUpdateInternal(BaseModel):
    uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            min_length=36,
            max_length=36,
            pattern="^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the tier to update. Must be a valid UUIDv4.",
        ),
    ]


class TierDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TierRestoreDeleted(BaseModel):
    is_deleted: bool = False
