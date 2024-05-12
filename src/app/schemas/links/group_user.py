import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema
from ...models.links.group_user import UserRole


class GroupUserBase(BaseModel):
    user_role: Annotated[
        UserRole,
        Field(examples=[role for role in UserRole], description="User role."),
    ]


class GroupUserExternal(GroupUserBase):
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Group UUID must be a valid UUIDv4.",
        ),
    ]
    user_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="User UUID must be a valid UUIDv4.",
        ),
    ]


class GroupUserInternal(GroupUserExternal):
    group_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Group ID must be a valid integer.",
        ),
    ]
    user_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="User ID must be a valid integer.",
        ),
    ]


class GroupUser(TimestampSchema, GroupUserInternal):
    pass


class GroupUserRead(GroupUserExternal):
    pass


class GroupUserCreate(GroupUserExternal):
    model_config = ConfigDict(extra="forbid")


class GroupUserCreateInternal(GroupUserInternal):
    model_config = ConfigDict(extra="forbid")


class GroupUserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_role: Annotated[
        UserRole,
        Field(examples=[role for role in UserRole], description="User role."),
    ]


class GroupUserUpdateInternal(GroupUserUpdate):
    pass


class GroupUserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
