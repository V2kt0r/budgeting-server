import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class TransactionReceiptBase(BaseModel):
    pass


class TransactionReceiptExternal(TransactionReceiptBase):
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction UUID must be a valid UUIDv4.",
        ),
    ]
    receipt_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Receipt UUID must be a valid UUIDv4.",
        ),
    ]


class TransactionReceiptInternal(TransactionReceiptBase):
    transaction_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction ID must be a valid integer.",
        ),
    ]
    receipt_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Receipt ID must be a valid integer.",
        ),
    ]


class TransactionReceipt(TimestampSchema, TransactionReceiptInternal):
    pass


class TransactionReceiptRead(TransactionReceiptExternal):
    pass


class TransactionReceiptCreate(TransactionReceiptExternal):
    model_config = ConfigDict(extra="forbid")


class TransactionReceiptCreateInternal(TransactionReceiptInternal):
    model_config = ConfigDict(extra="forbid")


class TransactionReceiptUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransactionReceiptUpdateInternal(TransactionReceiptUpdate):
    pass


class TransactionReceiptDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
