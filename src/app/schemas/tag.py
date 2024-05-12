from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)


class TagBase(BaseModel):
    tag_name: Annotated[
        str,
        Field(
            examples=[
                "Non-essential",
                "Essential",
                "Fast food",
            ],
            description="Name of the tag.",
        ),
    ]


class TagBaseExternal(TagBase):
    pass


class TagBaseInternal(TagBaseExternal):
    pass


class Tag(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    TagBaseInternal,
):
    pass


class TagRead(UUIDSchema, TagBaseExternal):
    pass


class TagCreate(TagBaseExternal):
    model_config = ConfigDict(extra="forbid")


class TagCreateInternal(TagCreate):
    pass


class TagUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: Annotated[
        str | None,
        Field(
            examples=[
                "Non-essential",
                "Essential",
                "Fast food",
            ],
            description="Name of the tag.",
        ),
    ] = None


class TagUpdateInternal(TagUpdate):
    pass


class TagDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
