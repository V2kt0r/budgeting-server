import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class UserPurchaseCategoryBase(BaseModel):
    pass


class UserPurchaseCategoryBaseExternal(UserPurchaseCategoryBase):
    user_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="User UUID must be a valid UUIDv4.",
        ),
    ]
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Purchase category UUID must be a valid UUIDv4.",
        ),
    ]


class UserPurchaseCategoryBaseInternal(UserPurchaseCategoryBaseExternal):
    user_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="User ID must be a valid integer.",
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


class UserPurchaseCategory(TimestampSchema, UserPurchaseCategoryBaseInternal):
    pass


class UserPurchaseCategoryRead(UserPurchaseCategoryBaseExternal):
    pass


class UserPurchaseCategoryCreate(UserPurchaseCategoryBaseExternal):
    model_config = ConfigDict(extra="forbid")


class UserPurchaseCategoryCreateInternal(UserPurchaseCategoryBaseInternal):
    model_config = ConfigDict(extra="forbid")


class UserPurchaseCategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserPurchaseCategoryUpdateInternal(UserPurchaseCategoryUpdate):
    pass


class UserPurchaseCategoryDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
