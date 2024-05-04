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
from ...crud.crud_groups import crud_groups
from ...crud.crud_purchase_categories import crud_purchase_categories
from ...crud.crud_tags import crud_tags
from ...crud.crud_transactions import crud_transactions
from ...crud.links.crud_group_purchase_category import (
    crud_group_purchase_category,
)
from ...crud.links.crud_group_user import crud_group_user
from ...crud.links.crud_transaction_tag import crud_transaction_tag
from ...crud.links.crud_user_purchase_category import (
    crud_user_purchase_category,
)
from ...crud.links.crud_user_tag import crud_user_tag
from ...crud.links.crud_user_transaction import crud_user_transaction
from ...models.links.group_purchase_category import (
    GroupPurchaseCategory as GroupPurchaseCategoryModel,
)
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
from ...schemas.group import Group as GroupSchema
from ...schemas.links.group_purchase_category import (
    GroupPurchaseCategoryCreateInternal,
)
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

router = APIRouter(tags=["Group Purchase Category"])


@router.post(
    "/group/{group_uuid}/purchase-category",
    response_model=PurchaseCategoryRead,
    status_code=201,
)
async def create_group_purchase_category(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="UUID of the group to which the purchase category belongs.",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    purchase_category_create: Annotated[PurchaseCategoryCreate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Check if group exists
    group_schema: GroupSchema | None = await crud_groups.get(
        db=db,
        uuid=group_uuid,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=GroupSchema,
    )
    if group_schema is None:
        raise NotFoundException("The group with this UUID does not exist.")

    # Check if user is a member of the group
    user_is_member: bool = await crud_group_user.exists(
        db=db, user_id=current_user.id, group_id=group_schema.id
    )
    if not user_is_member:
        raise ForbiddenException(
            "You are not a member of the group with this UUID."
        )

    # Create the purchase category
    purchase_category_model: PurchaseCategoryModel = (
        await crud_purchase_categories.create(
            db=db,
            object=PurchaseCategoryCreateInternal.model_validate(
                purchase_category_create.model_dump()
            ),
        )
    )

    # Create the group purchase category link
    group_purchase_category_model: GroupPurchaseCategoryModel = (
        await crud_group_purchase_category.create(
            db=db,
            object=GroupPurchaseCategoryCreateInternal(
                group_id=group_schema.id,
                group_uuid=group_schema.uuid,
                purchase_category_id=purchase_category_model.id,
                purchase_category_uuid=purchase_category_model.uuid,
            ),
        )
    )

    return purchase_category_model


@router.get(
    "/group/{group_uuid}/purchase-category",
    response_model=PaginatedListResponse[PurchaseCategoryRead],
)
async def get_group_purchase_categories(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="UUID of the group to which the purchase categories belong.",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = Query(ge=1, default=1),
    items_per_page: int = Query(ge=1, le=100, default=10),
) -> Any:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(
        db=db, uuid=group_uuid, is_deleted=False
    )
    if not group_exists:
        raise NotFoundException("The group with this UUID does not exist.")

    # Check if user is a member of the group
    user_is_member: bool = await crud_group_user.exists(
        db=db,
        user_id=current_user.id,
        group_uuid=group_uuid,
    )
    if not user_is_member:
        raise ForbiddenException(
            "You are not a member of the group with this UUID."
        )

    # Get the purchase categories
    group_purchase_category_join_config = JoinConfig(
        model=GroupPurchaseCategoryModel,
        join_on=(
            GroupPurchaseCategoryModel.purchase_category_id
            == PurchaseCategoryModel.id
        ),
        schema_to_select=BaseModel,
        filters={"group_uuid": group_uuid},
    )
    crud_data: dict[str, Any] = await crud_purchase_categories.get_multi_joined(
        db=db,
        is_deleted=False,
        joins_config=[group_purchase_category_join_config],
        return_as_model=True,
        schema_to_select=PurchaseCategoryRead,
    )
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )
