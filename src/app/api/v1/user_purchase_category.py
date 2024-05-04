import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Path, Query, Request
from fastcrud import JoinConfig
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from pydantic import BaseModel
from sqlalchemy import func, not_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    ForbiddenException,
    NotFoundException,
)
from ...core.schemas.utils import Message
from ...crud.crud_purchase_categories import crud_purchase_categories
from ...crud.crud_tags import crud_tags
from ...crud.crud_transactions import crud_transactions
from ...crud.links.crud_transaction_tag import crud_transaction_tag
from ...crud.links.crud_user_purchase_category import (
    crud_user_purchase_category,
)
from ...crud.links.crud_user_tag import crud_user_tag
from ...crud.links.crud_user_transaction import crud_user_transaction
from ...models.links.transaction_tag import (
    TransactionTag as TransactionTagModel,
)
from ...models.links.user_purchase_category import (
    UserPurchaseCategory as UserPurchaseCategoryModel,
)
from ...models.links.user_tag import UserTag as UserTagModel
from ...models.links.user_transaction import (
    UserTransaction as UserTransactionModel,
)
from ...models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ...models.tag import Tag as TagModel
from ...models.transaction import Transaction as TransactionModel
from ...schemas.links.transaction_tag import TransactionTagCreateInternal
from ...schemas.links.user_purchase_category import (
    UserPurchaseCategoryCreateInternal,
)
from ...schemas.links.user_tag import UserTagCreateInternal
from ...schemas.links.user_transaction import UserTransactionCreateInternal
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ...schemas.purchase_category import (
    PurchaseCategoryCreate,
    PurchaseCategoryCreateInternal,
    PurchaseCategoryRead,
    PurchaseCategoryUpdate,
)
from ...schemas.tag import Tag as TagSchema
from ...schemas.tag import TagCreateInternal, TagRead
from ...schemas.transaction import Transaction as TransactionSchema
from ...schemas.transaction import (
    TransactionCreate,
    TransactionCreateInternal,
    TransactionRead,
    TransactionUpdate,
    TransactionUpdateInternal,
)
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user

router = APIRouter(tags=["User Purchase Category"])


@router.post(
    "/purchase-category", response_model=PurchaseCategoryRead, status_code=201
)
async def create_purchase_category(
    *,
    request: Request,
    purchase_category_create: Annotated[PurchaseCategoryCreate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Create the purchase category
    purchase_category_model: PurchaseCategoryModel = (
        await crud_purchase_categories.create(
            db=db,
            object=PurchaseCategoryCreateInternal.model_validate(
                purchase_category_create.model_dump()
            ),
        )
    )

    # Create the user purchase category link
    user_purchase_category_model: UserPurchaseCategoryModel = (
        await crud_user_purchase_category.create(
            db=db,
            object=UserPurchaseCategoryCreateInternal(
                user_id=current_user.id,
                user_uuid=current_user.uuid,
                purchase_category_id=purchase_category_model.id,
                purchase_category_uuid=purchase_category_model.uuid,
            ),
        )
    )

    return purchase_category_model


@router.get(
    "/purchase-category",
    response_model=PaginatedListResponse[PurchaseCategoryRead],
)
async def get_purchase_categories(
    *,
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = Query(ge=1, default=1),
    items_per_page: int = Query(ge=1, le=100, default=10),
) -> Any:
    # Get the purchase categories
    user_purchase_category_join_config = JoinConfig(
        model=UserPurchaseCategoryModel,
        join_on=(
            UserPurchaseCategoryModel.purchase_category_id
            == PurchaseCategoryModel.id
        ),
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    crud_data: dict[str, Any] = await crud_purchase_categories.get_multi_joined(
        db=db,
        is_deleted=False,
        joins_config=[user_purchase_category_join_config],
        return_as_model=True,
        schema_to_select=PurchaseCategoryRead,
    )
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )


@router.put(
    "/purchase-category/{purchase_category_uuid}", response_model=Message
)
async def update_purchase_category(
    *,
    request: Request,
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the purchase category to update.",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    purchase_category_update: Annotated[PurchaseCategoryUpdate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=purchase_category_uuid, is_deleted=False
    )
    if not purchase_category_exists:
        raise NotFoundException(
            "The purchase category with this UUID does not exist."
        )

    # Check if user has access to purchase category
    user_purchase_category_exists: bool = (
        await crud_user_purchase_category.exists(
            db=db,
            user_id=current_user.id,
            purchase_category_uuid=purchase_category_uuid,
        )
    )
    if not user_purchase_category_exists:
        raise ForbiddenException(
            "You do not have access to this purchase category."
        )

    # Update the purchase category
    await crud_purchase_categories.update(
        db=db,
        uuid=purchase_category_uuid,
        object=PurchaseCategoryUpdate.model_validate(
            purchase_category_update.model_dump()
        ),
    )
    return Message(message="The purchase category has been updated.")


@router.delete(
    "/purchase-category/{purchase_category_uuid}", response_model=Message
)
async def delete_purchase_category(
    *,
    request: Request,
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the purchase category to delete.",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=purchase_category_uuid, is_deleted=False
    )
    if not purchase_category_exists:
        raise NotFoundException(
            "The purchase category with this UUID does not exist."
        )

    # Check if user has access to purchase category
    user_purchase_category_exists: bool = (
        await crud_user_purchase_category.exists(
            db=db,
            user_id=current_user.id,
            purchase_category_uuid=purchase_category_uuid,
        )
    )
    if not user_purchase_category_exists:
        raise ForbiddenException(
            "You do not have access to this purchase category."
        )

    # Check if purchase category is linked to any transactions
    transactions_linked: bool = await crud_transactions.exists(
        db=db, purchase_category_uuid=purchase_category_uuid
    )
    if transactions_linked:
        raise ForbiddenException(
            "The purchase category is linked to transactions."
        )

    # Delete the purchase category
    await crud_purchase_categories.delete(db=db, uuid=purchase_category_uuid)
    return Message(message="The purchase category has been deleted.")
