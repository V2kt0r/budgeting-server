import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class UserTagBase(BaseModel):
    pass


class UserTagExternal(UserTagBase):
    user_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="User UUID must be a valid UUIDv4.",
        ),
    ]
    tag_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tag UUID must be a valid UUIDv4.",
        ),
    ]


class UserTagInternal(UserTagExternal):
    user_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="User ID must be a valid integer.",
        ),
    ]
    tag_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Tag ID must be a valid integer.",
        ),
    ]


class UserTag(TimestampSchema, UserTagInternal):
    pass


class UserTagRead(UserTagExternal):
    pass


class UserTagCreate(UserTagExternal):
    model_config = ConfigDict(extra="forbid")


class UserTagCreateInternal(UserTagInternal):
    model_config = ConfigDict(extra="forbid")


class UserTagUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserTagUpdateInternal(UserTagUpdate):
    pass


class UserTagDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
