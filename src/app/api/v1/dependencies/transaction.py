import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import Depends, Path
from fastcrud import JoinConfig
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import (
    ForbiddenException,
    NotFoundException,
)
from ....crud.crud_transactions import crud_transactions
from ....models.links.group_transaction import (
    GroupTransaction as GroupTransactionModel,
)
from ....models.links.user_transaction import (
    UserTransaction as UserTransactionModel,
)
from ....models.transaction import Transaction as TransactionModel
from ....schemas.group import Group as GroupSchema
from ....schemas.transaction import Transaction as TransactionSchema
from ....schemas.user import User as UserSchema
from ...dependencies import get_current_user
from .group import get_non_deleted_user_group


async def get_non_deleted_transaction_uuid(
    *,
    transaction_uuid: uuid_pkg.UUID = Path(
        examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        description="UUID of the transaction",
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID:
    # Check if transaction exists
    transaction_exists: bool = await crud_transactions.exists(
        db=db, uuid=transaction_uuid, is_deleted=False
    )
    if not transaction_exists:
        raise NotFoundException(
            "Transaction does not exist or has been deleted."
        )

    return transaction_uuid


async def get_non_deleted_user_transaction(
    transaction_uuid: Annotated[
        uuid_pkg.UUID, Depends(get_non_deleted_transaction_uuid)
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TransactionSchema:
    # Check if user has access to transaction
    user_transaction_join_config = JoinConfig(
        model=UserTransactionModel,
        join_on=UserTransactionModel.transaction_id == TransactionModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    transaction_dict: dict[str, Any] | None = (
        await crud_transactions.get_joined(
            db=db,
            uuid=transaction_uuid,
            is_deleted=False,
            joins_config=[user_transaction_join_config],
            schema_to_select=TransactionSchema,
        )
    )
    if transaction_dict is None:
        raise ForbiddenException("User does not have access to transaction.")

    return TransactionSchema.model_validate(transaction_dict)


async def get_non_deleted_group_transaction(
    transaction_uuid: Annotated[
        uuid_pkg.UUID, Depends(get_non_deleted_transaction_uuid)
    ],
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TransactionSchema:
    # Check if group has access to transaction
    group_transaction_join_config = JoinConfig(
        model=GroupTransactionModel,
        join_on=GroupTransactionModel.transaction_id == TransactionModel.id,
        schema_to_select=BaseModel,
        filters={"group_id": group_schema.id},
    )
    transaction_dict: dict[str, Any] | None = (
        await crud_transactions.get_joined(
            db=db,
            uuid=transaction_uuid,
            is_deleted=False,
            joins_config=[group_transaction_join_config],
            schema_to_select=TransactionSchema,
        )
    )
    if transaction_dict is None:
        raise ForbiddenException("Group does not have access to transaction.")

    return TransactionSchema.model_validate(transaction_dict)
