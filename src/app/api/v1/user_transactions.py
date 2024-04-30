import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastcrud import JoinConfig
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    CustomException,
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from ...crud.crud_groups import crud_groups
from ...crud.crud_purchase_categories import crud_purchase_categories
from ...crud.crud_tags import crud_tags
from ...crud.crud_transactions import crud_transactions
from ...crud.crud_users import crud_users
from ...models.group import Group as GroupModel
from ...models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ...models.tag import Tag as TagModel
from ...models.transaction import Transaction as TransactionModel
from ...models.transaction import association_table_transaction_tag
from ...models.user import User as UserModel
from ...models.user_group_link import UserGroupLink as UserGroupLinkModel
from ...schemas.group import Group as GroupSchema
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ...schemas.tag import Tag as TagSchema
from ...schemas.tag import TagCreateInternal, TagRead
from ...schemas.transaction import (
    TransactionCreate,
    TransactionCreateInternal,
    TransactionRead,
)
from ...schemas.transaction_group_link import (
    TransactionGroupLinkCreate,
    TransactionGroupLinkCreateInternal,
)
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user

router = APIRouter(tags=["transactions"])


@router.post(
    "/transaction",
    response_model=TransactionRead,
    status_code=201,
)
async def write_user_transaction(
    *,
    request: Request,
    transaction_create: TransactionCreate,
    tag_names: Annotated[list[str] | None, Query()] = None,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=transaction_create.purchase_category_uuid, is_deleted=False
    )
    if not purchase_category_exists:
        raise NotFoundException(
            f"Purchase category with uuid {transaction_create.purchase_category_uuid} not found."
        )

    # Check if user has access to purchase category
    purchase_category: PurchaseCategorySchema | None = next(
        (
            purchase_category
            for purchase_category in current_user.purchase_categories
            if purchase_category.uuid
            == transaction_create.purchase_category_uuid
        ),
        None,
    )
    if purchase_category is None:
        raise ForbiddenException()

    # Check tags and create if necessary
    if tag_names is None:
        tag_names = []
    for tag_name in tag_names:
        tag: TagSchema | None = next(
            (
                tag_
                for tag_ in current_user.tags
                if tag_.tag_name == tag_name.strip()
            ),
            None,
        )
        if tag is None:
            tag_create_internal = TagCreateInternal(tag_name=tag_name.strip())
            tag_model: TagModel = await crud_tags.create(
                db=db, object=tag_create_internal
            )
            tag = TagSchema.model_validate(tag_model)
        current_user.tags.append(tag)
    await crud_users.update(db=db, object=current_user.model_dump())

    transaction_create_internal = TransactionCreateInternal(
        **transaction_create.model_dump(),
        purchase_category_id=purchase_category.id,
        purchase_category_uuid=purchase_category.uuid,
        tags=current_user.tags,
    )
    transaction: TransactionModel = await crud_transactions.create(
        db=db, object=transaction_create_internal
    )
    return transaction


@router.get(
    "/transactions", response_model=PaginatedListResponse[TransactionRead]
)
async def get_user_transactions(
    *,
    request: Request,
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID | None,
        Query(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the purchase category to filter transactions by",
        ),
    ] = None,
    tag_names: list[str] = Query(
        examples=[
            ["Essentials", "Fast food"],
            ["Non-essentials", "Car related"],
        ],
        description="List of tag names to filter transactions by",
        default_factory=lambda: [],
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Any:
    # Check if purchase category exists
    purchase_category: PurchaseCategorySchema | None = None
    if purchase_category_uuid is not None:
        purchase_category_exists: bool = await crud_purchase_categories.exists(
            db=db, uuid=purchase_category_uuid, is_deleted=False
        )
        if not purchase_category_exists:
            raise NotFoundException(
                "Purchase category does not exist or has been deleted."
            )

        # Check if user has access to purchase category
        purchase_category = next(
            (
                purchase_category
                for purchase_category in current_user.purchase_categories
                if purchase_category.uuid == purchase_category_uuid
            ),
            None,
        )
        if purchase_category is None:
            raise ForbiddenException()

    # Filter tags for existing tags
    tags = []
    for tag_name in tag_names:
        tag: TagSchema | None = next(
            (
                tag_
                for tag_ in current_user.tags
                if tag_.tag_name == tag_name.strip()
            ),
            None,
        )
        if tag is not None:
            tags.append(tag)

    # Get transactions
    join_configs = []
    if purchase_category is not None:
        purcahse_category_join_config = JoinConfig(
            model=PurchaseCategoryModel,
            join_on=(
                PurchaseCategoryModel.id
                == TransactionModel.purchase_category_uuid
            ),
            schema_to_select=BaseModel,
            filters={"uuid": purchase_category.uuid},
        )
        join_configs.append(purcahse_category_join_config)
    if tag_names is not None:
        join_on_field: Any = None
        if len(tags) == 0:
            join_on_field = (
                TransactionModel.id
                == association_table_transaction_tag.c.transaction_id
            )
        else:
            join_on_field = and_(
                TransactionModel.id
                == association_table_transaction_tag.c.transaction_id,
                association_table_transaction_tag.c.tag_id.in_(
                    [tag.id for tag in tags]
                ),
            )
        tag_join_configs = JoinConfig(
            model=association_table_transaction_tag,
            join_on=join_on_field,
            schema_to_select=BaseModel,
        )
        join_configs.append(tag_join_configs)
    crud_data: dict[str, Any] = await crud_transactions.get_multi_joined(
        db=db,
        return_as_model=True,
        schema_to_select=TransactionRead,
        joins_config=join_configs,
        offset=compute_offset(page=page, items_per_page=items_per_page),
        limit=items_per_page,
        is_deleted=False,
    )
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )
