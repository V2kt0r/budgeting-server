from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)
from ..schemas.links.group_user import GroupUserBase


class GroupBase(BaseModel):
    name: Annotated[
        str, Field(examples=["My Group"], description="The name of the group")
    ]


class GroupBaseExternal(GroupBase):
    pass


class GroupBaseInternal(GroupBaseExternal):
    pass


class Group(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    GroupBaseInternal,
):
    pass


class GroupRead(UUIDSchema, GroupBaseExternal):
    pass


class GroupReadWithUserRole(GroupUserBase, GroupRead):
    pass


class GroupCreate(GroupBaseExternal):
    pass


class GroupCreateInternal(GroupBaseInternal):
    pass


class GroupUpdate(BaseModel):
    name: Annotated[
        str | None,
        Field(
            examples=["My Group"],
            description="The name of the group",
        ),
    ] = None


class GroupUpdateInternal(GroupUpdate):
    pass


class GroupDelete(BaseModel):
    pass
