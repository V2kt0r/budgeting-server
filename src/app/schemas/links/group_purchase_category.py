import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class GroupPurchaseCategoryBase(BaseModel):
    pass


class GroupPurchaseCategoryBaseExternal(GroupPurchaseCategoryBase):
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Group UUID must be a valid UUIDv4.",
        ),
    ]
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Purchase category UUID must be a valid UUIDv4.",
        ),
    ]


class GroupPurchaseCategoryBaseInternal(GroupPurchaseCategoryBaseExternal):
    group_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Group ID must be a valid integer.",
        ),
    ]
    purchase_category_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Purchase category ID must be a valid integer.",
        ),
    ]


class GroupPurchaseCategory(TimestampSchema, GroupPurchaseCategoryBaseInternal):
    pass


class GroupPurchaseCategoryRead(GroupPurchaseCategoryBaseExternal):
    pass


class GroupPurchaseCategoryCreate(GroupPurchaseCategoryBaseExternal):
    model_config = ConfigDict(extra="forbid")


class GroupPurchaseCategoryCreateInternal(GroupPurchaseCategoryBaseInternal):
    model_config = ConfigDict(extra="forbid")


class GroupPurchaseCategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GroupPurchaseCategoryUpdateInternal(GroupPurchaseCategoryUpdate):
    pass


class GroupPurchaseCategoryDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
