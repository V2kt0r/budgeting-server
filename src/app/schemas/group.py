from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)


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


class GroupRead(GroupBaseExternal):
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
