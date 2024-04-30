import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class TransactionTransactionItemBase(BaseModel):
    pass


class TransactionTransactionItemExternal(TransactionTransactionItemBase):
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction UUID must be a valid UUIDv4.",
        ),
    ]
    transaction_item_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction item UUID must be a valid UUIDv4.",
        ),
    ]


class TransactionTransactionItemInternal(TransactionTransactionItemBase):
    transaction_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction ID must be a valid integer.",
        ),
    ]
    transaction_item_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction item ID must be a valid integer.",
        ),
    ]


class TransactionTransactionItem(
    TimestampSchema, TransactionTransactionItemInternal
):
    pass


class TransactionTransactionItemRead(TransactionTransactionItemExternal):
    pass


class TransactionTransactionItemCreate(TransactionTransactionItemExternal):
    model_config = ConfigDict(extra="forbid")


class TransactionTransactionItemCreateInternal(
    TransactionTransactionItemInternal
):
    model_config = ConfigDict(extra="forbid")


class TransactionTransactionItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransactionTransactionItemUpdateInternal(
    TransactionTransactionItemUpdate
):
    pass


class TransactionTransactionItemDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
