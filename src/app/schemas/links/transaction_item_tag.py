import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class TransactionItemTagBase(BaseModel):
    pass


class TransactionItemTagExternal(TransactionItemTagBase):
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction item UUID must be a valid UUIDv4.",
        ),
    ]
    tag_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tag UUID must be a valid UUIDv4.",
        ),
    ]


class TransactionItemTagInternal(TransactionItemTagBase):
    transaction_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction item ID must be a valid integer.",
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


class TransactionItemTag(TimestampSchema, TransactionItemTagInternal):
    pass


class TransactionItemTagRead(TransactionItemTagExternal):
    pass


class TransactionItemTagCreate(TransactionItemTagExternal):
    model_config = ConfigDict(extra="forbid")


class TransactionItemTagCreateInternal(TransactionItemTagInternal):
    model_config = ConfigDict(extra="forbid")


class TransactionItemTagUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransactionItemTagUpdateInternal(TransactionItemTagUpdate):
    pass


class TransactionItemTagDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
