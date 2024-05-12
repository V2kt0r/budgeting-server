from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Query, Request
from fastcrud import JoinConfig
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    CustomException,
    UnprocessableEntityException,
)
from ...core.schemas.utils import Message
from ...crud.crud_transaction_item import crud_transaction_item
from ...crud.crud_transactions import crud_transactions
from ...crud.links.crud_transaction_transaction_item import (
    crud_transaction_transaction_item,
)
from ...crud.links.crud_user_transaction import crud_user_transaction
from ...models.links.user_transaction import (
    UserTransaction as UserTransactionModel,
)
from ...models.transaction import Transaction as TransactionModel
from ...schemas.links.user_transaction import UserTransactionCreateInternal
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ...schemas.transaction import Transaction as TransactionSchema
from ...schemas.transaction import (
    TransactionCreate,
    TransactionCreateInternal,
    TransactionRead,
    TransactionUpdate,
    TransactionUpdateInternal,
)
from ...schemas.transaction_item import TransactionItem as TransactionItemSchema
from ...schemas.transaction_item import TransactionItemCreate
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user
from .dependencies.purchase_category import (
    get_optional_non_deleted_user_purchase_category,
)
from .dependencies.transaction import get_non_deleted_user_transaction
from .dependencies.transaction_item import (
    create_user_transaction_items,
    get_transaction_items_with_data,
    get_user_transaction_items,
    remove_user_transaction_items,
)

router = APIRouter(tags=["Transactions"])


@router.post("/transaction", response_model=TransactionRead, status_code=201)
async def create_user_transaction(
    *,
    request: Request,
    transaction_create: TransactionCreate,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Get purchase category
    purchase_category_schema: PurchaseCategorySchema | None = (
        await get_optional_non_deleted_user_purchase_category(
            purchase_category_uuid=transaction_create.purchase_category_uuid,
            current_user=current_user,
            db=db,
        )
    )

    # Tags and purchase category should only be provided if transaction_items list is empty
    if len(transaction_create.transaction_items) > 0:
        if purchase_category_schema is not None:
            raise UnprocessableEntityException(
                "Purchase category should be None if transaction_items list is not empty"
            )
        if len(transaction_create.tag_names) > 0:
            raise UnprocessableEntityException(
                "Tags should be empty if transaction_items list is not empty"
            )
    else:
        if purchase_category_schema is None:
            raise UnprocessableEntityException(
                "Purchase category should be provided if transaction_items list is empty"
            )
        if len(transaction_create.tag_names) == 0:
            raise UnprocessableEntityException(
                "Tags should be provided if transaction_items list is empty"
            )

    # If there are no transaction_items proveded, create a default transaction item
    if len(transaction_create.transaction_items) == 0:
        if purchase_category_schema is None:
            raise CustomException(detail="This should not happen. Error: 2")
        transaction_item_create = TransactionItemCreate(
            name=transaction_create.name,
            amount=transaction_create.amount,
            description=transaction_create.description,
            tag_names=transaction_create.tag_names,
            purchase_category_uuid=purchase_category_schema.uuid,
        )
        transaction_create.transaction_items.append(transaction_item_create)

    # Check if transaction_create.amount is the sum of all transaction_items.amount
    if (
        sum(
            [
                transaction_item.amount
                for transaction_item in transaction_create.transaction_items
            ]
        )
        != transaction_create.amount
    ):
        raise UnprocessableEntityException(
            "Transaction amount should be the sum of all transaction items amount"
        )

    # Create transaction
    transaction_create_internal = TransactionCreateInternal(
        **transaction_create.model_dump(
            exclude={"purchase_category_uuid", "tag_names", "transaction_items"}
        ),
    )
    transaction_model: TransactionModel = await crud_transactions.create(
        db=db, object=transaction_create_internal
    )

    # Create user transaction
    user_transaction_create_internal = UserTransactionCreateInternal(
        user_id=current_user.id,
        user_uuid=current_user.uuid,
        transaction_id=transaction_model.id,
        transaction_uuid=transaction_model.uuid,
    )
    await crud_user_transaction.create(
        db=db, object=user_transaction_create_internal
    )

    await create_user_transaction_items(
        transaction=transaction_model,
        transaction_items=transaction_create.transaction_items,
        current_user=current_user,
        db=db,
    )

    transaction_dict = vars(transaction_model)
    transaction_dict["transaction_items"] = (
        await get_transaction_items_with_data(
            transaction_dict=transaction_dict, db=db
        )
    )

    return transaction_dict


@router.get(
    "/transaction", response_model=PaginatedListResponse[TransactionRead]
)
async def get_user_transactions(
    *,
    request: Request,
    before: datetime | None = Query(
        default=None,
        description="Get transactions before this date",
        examples=[datetime.now(UTC)],
    ),
    after: datetime | None = Query(
        default=None,
        description="Get transactions after this date",
        examples=[datetime.now(UTC) - timedelta(days=7)],
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Any:
    # Get transactions
    kwargs = {}
    if before is not None:
        kwargs["timestamp__lt"] = before
    if after is not None:
        kwargs["timestamp__gt"] = after

    user_transaction_join_config = JoinConfig(
        model=UserTransactionModel,
        join_on=UserTransactionModel.transaction_id == TransactionModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    crud_data: dict[str, Any] = await crud_transactions.get_multi_joined(
        db=db,
        is_deleted=False,
        **kwargs,
        joins_config=[user_transaction_join_config],
        return_as_model=False,
        schema_to_select=TransactionSchema,
        offset=compute_offset(page=page, items_per_page=items_per_page),
        limit=items_per_page,
    )
    for transaction in crud_data["data"]:
        transaction["transaction_items"] = (
            await get_transaction_items_with_data(
                transaction_dict=transaction, db=db
            )
        )

    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )


@router.get("/transaction/{transaction_uuid}", response_model=TransactionRead)
async def get_transaction(
    *,
    request: Request,
    transaction_schema: Annotated[
        TransactionSchema, Depends(get_non_deleted_user_transaction)
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    transaction_dict: dict[str, Any] = transaction_schema.model_dump()

    transaction_dict["transaction_items"] = (
        await get_transaction_items_with_data(
            transaction_dict=transaction_dict, db=db
        )
    )

    return transaction_dict


@router.put("/transaction/{transaction_uuid}", response_model=Message)
async def update_transaction(
    *,
    request: Request,
    transaction_schema: Annotated[
        TransactionSchema, Depends(get_non_deleted_user_transaction)
    ],
    transaction_update: Annotated[TransactionUpdate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Get purchase category
    purchase_category_schema: PurchaseCategorySchema | None = (
        await get_optional_non_deleted_user_purchase_category(
            purchase_category_uuid=transaction_update.purchase_category_uuid,
            current_user=current_user,
            db=db,
        )
    )

    # Tags and purchase category should only be provided if transaction_items list is empty
    if len(transaction_update.transaction_items) > 0:
        if purchase_category_schema is not None:
            raise UnprocessableEntityException(
                "Purchase category should be None if transaction_items list is not empty"
            )
        if len(transaction_update.tag_names) > 0:
            raise UnprocessableEntityException(
                "Tags should be empty if transaction_items list is not empty"
            )
    else:
        if purchase_category_schema is None:
            raise UnprocessableEntityException(
                "Purchase category should be provided if transaction_items list is empty"
            )
        if len(transaction_update.tag_names) == 0:
            raise UnprocessableEntityException(
                "Tags should be provided if transaction_items list is empty"
            )

    # Check if transaction_create.amount is the sum of all transaction_items.amount
    if (
        sum(
            [
                transaction_item.amount
                for transaction_item in transaction_update.transaction_items
            ]
        )
        != transaction_update.amount
    ):
        raise UnprocessableEntityException(
            "Transaction amount should be the sum of all transaction items amount"
        )

    # If there are no transaction_items proveded, create a default transaction item
    if len(transaction_update.transaction_items) == 0:
        if purchase_category_schema is None:
            raise CustomException(detail="This should not happen. Error: 2")
        transaction_item_create = TransactionItemCreate(
            name=transaction_update.name,
            amount=transaction_update.amount,
            description=transaction_update.description,
            tag_names=transaction_update.tag_names,
            purchase_category_uuid=purchase_category_schema.uuid,
        )
        transaction_update.transaction_items.append(transaction_item_create)

    # Update transaction
    transaction_update_internal = TransactionUpdateInternal(
        **transaction_update.model_dump(
            exclude={"purchase_category_uuid", "tag_names", "transaction_items"}
        )
    )
    await crud_transactions.update(
        db=db,
        uuid=transaction_schema.uuid,
        object=transaction_update_internal.model_dump(),
    )
    await remove_user_transaction_items(
        transaction=transaction_schema,
        current_user=current_user,
        db=db,
    )
    await create_user_transaction_items(
        transaction=transaction_schema,
        transaction_items=transaction_update.transaction_items,
        current_user=current_user,
        db=db,
    )
    # TODO: check if removing and creating transaction items is necessary for performance
    # TODO: clean up tags that are no longer in use
    return Message(message="Transaction updated successfully.")


@router.delete("/transaction/{transaction_uuid}", response_model=Message)
async def delete_transaction(
    *,
    request: Request,
    transaction_schema: Annotated[
        TransactionSchema, Depends(get_non_deleted_user_transaction)
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Get transaction items
    transaction_items: list[TransactionItemSchema] = (
        await get_user_transaction_items(
            transaction=transaction_schema,
            current_user=current_user,
            db=db,
        )
    )
    for transaction_item in transaction_items:
        await crud_transaction_transaction_item.delete(
            db=db,
            transaction_id=transaction_schema.id,
            transaction_item_id=transaction_item.id,
        )
        await crud_transaction_item.delete(db=db, uuid=transaction_item.uuid)

    # Delete transaction
    await crud_transactions.delete(db=db, uuid=transaction_schema.uuid)
    # TODO: clean up tags that are no longer in use
    return Message(message="Transaction deleted successfully.")
