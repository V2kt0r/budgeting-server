import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import TimestampSchema


class UserTransactionBase(BaseModel):
    pass


class UserTransactionExternal(UserTransactionBase):
    user_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="User UUID must be a valid UUIDv4.",
        ),
    ]
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction UUID must be a valid UUIDv4.",
        ),
    ]


class UserTransactionInternal(UserTransactionExternal):
    user_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="User ID must be a valid integer.",
        ),
    ]
    transaction_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction ID must be a valid integer.",
        ),
    ]


class UserTransaction(TimestampSchema, UserTransactionInternal):
    pass


class UserTransactionRead(UserTransactionExternal):
    pass


class UserTransactionCreate(UserTransactionExternal):
    model_config = ConfigDict(extra="forbid")


class UserTransactionCreateInternal(UserTransactionInternal):
    model_config = ConfigDict(extra="forbid")


class UserTransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserTransactionUpdateInternal(UserTransactionUpdate):
    pass


class UserTransactionDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
