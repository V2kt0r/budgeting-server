import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class GroupTagBase(BaseModel):
    pass


class GroupTagExternal(GroupTagBase):
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Group UUID must be a valid UUIDv4.",
        ),
    ]
    tag_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tag UUID must be a valid UUIDv4.",
        ),
    ]


class GroupTagInternal(GroupTagBase):
    group_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Group ID must be a valid integer.",
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


class GroupTag(TimestampSchema, GroupTagInternal):
    pass


class GroupTagRead(GroupTagExternal):
    pass


class GroupTagCreate(GroupTagExternal):
    model_config = ConfigDict(extra="forbid")


class GroupTagCreateInternal(GroupTagInternal):
    model_config = ConfigDict(extra="forbid")


class GroupTagUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GroupTagUpdateInternal(GroupTagUpdate):
    pass


class GroupTagDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
