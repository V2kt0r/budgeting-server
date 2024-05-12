import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas.mixins import IDSchema, TimestampSchema, UUIDSchema


class GroupTransactionBase(BaseModel):
    pass


class GroupTransactionBaseExternal(GroupTransactionBase):
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Transaction UUID must be a valid UUIDv4.",
        ),
    ]
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Group UUID must be a valid UUIDv4.",
        ),
    ]
    created_by_user_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="User UUID must be a valid UUIDv4.",
        ),
    ]


class GroupTransactionBaseInternal(GroupTransactionBaseExternal):
    transaction_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Transaction ID must be a valid integer.",
        ),
    ]
    group_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="Group ID must be a valid integer.",
        ),
    ]
    created_by_user_id: Annotated[
        int,
        Field(
            ge=1,
            examples=[1, 2, 3],
            description="User ID must be a valid integer.",
        ),
    ]


class GroupTransaction(
    IDSchema, UUIDSchema, TimestampSchema, GroupTransactionBaseInternal
):
    pass


class GroupTransactionRead(UUIDSchema, GroupTransactionBaseExternal):
    pass


class GroupTransactionCreate(GroupTransactionBaseExternal):
    model_config = ConfigDict(extra="forbid")


class GroupTransactionCreateInternal(GroupTransactionBaseInternal):
    model_config = ConfigDict(extra="forbid")


class GroupTransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GroupTransactionUpdateInternal(GroupTransactionUpdate):
    pass


class GroupTransactionDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
