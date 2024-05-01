import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class TransactionTagBase(BaseModel):
    pass


class TransactionTagExternal(TransactionTagBase):
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction UUID must be a valid UUIDv4.",
        ),
    ]
    tag_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tag UUID must be a valid UUIDv4.",
        ),
    ]


class TransactionTagInternal(TransactionTagExternal):
    transaction_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction ID must be a valid integer.",
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


class TransactionTag(TimestampSchema, TransactionTagInternal):
    pass


class TransactionTagRead(TransactionTagExternal):
    pass


class TransactionTagCreate(TransactionTagExternal):
    model_config = ConfigDict(extra="forbid")


class TransactionTagCreateInternal(TransactionTagInternal):
    model_config = ConfigDict(extra="forbid")


class TransactionTagUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransactionTagUpdateInternal(TransactionTagUpdate):
    pass


class TransactionTagDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
