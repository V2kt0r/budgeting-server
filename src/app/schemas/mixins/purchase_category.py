import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, Field


class PurchaseCategoryIDSchema(BaseModel):
    purchase_category_id: Annotated[
        int,
        Field(
            title="Purchase category ID",
            description="Purchase category ID is a unique identifier for the purchase category.",
        ),
    ]


class PurchaseCategoryUUIDSchema(BaseModel):
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            title="Purchase category UUID",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Purchase category UUID must be a valid UUIDv4.",
        ),
    ]


class PurchaseCategoryOptionalUUIDSchema(BaseModel):
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            default=None,
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Purchase category UUID must be a valid UUIDv4.",
        ),
    ]


class PurchaseCategoryOptionalIDSchema(BaseModel):
    purchase_category_id: Annotated[
        int | None,
        Field(
            default=None,
            title="Purchase category ID",
            description="Purchase category ID is a unique identifier for the purchase category.",
        ),
    ]
