import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Request
from fastcrud import JoinConfig
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from pydantic import BaseModel
from sqlalchemy import func, not_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.links.group_purchase_category import (
    GroupPurchaseCategory as GroupPurchaseCategoryModel,
)

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    CustomException,
    ForbiddenException,
    NotFoundException,
)
from ...crud.crud_groups import crud_groups
from ...crud.crud_purchase_categories import crud_purchase_categories
from ...crud.crud_tags import crud_tags
from ...crud.crud_transactions import crud_transactions
from ...crud.links.crud_group_purchase_category import (
    crud_group_purchase_category,
)
from ...crud.links.crud_group_tag import crud_group_tag
from ...crud.links.crud_group_transaction import crud_group_transactions
from ...crud.links.crud_group_user import crud_group_user
from ...crud.links.crud_transaction_tag import crud_transaction_tag
from ...models.links.group_tag import GroupTag as GroupTagModel
from ...models.links.group_transaction import (
    GroupTransaction as GroupTransactionModel,
)
from ...models.links.transaction_tag import (
    TransactionTag as TransactionTagModel,
)
from ...models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ...models.tag import Tag as TagModel
from ...models.transaction import Transaction as TransactionModel
from ...schemas.group import Group as GroupSchema
from ...schemas.links.group_tag import GroupTagCreateInternal
from ...schemas.links.group_transaction import GroupTransactionCreateInternal
from ...schemas.links.transaction_tag import TransactionTagCreateInternal
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
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user

router = APIRouter(tags=["Group Transactions"])


@router.post(
    "/group/{group_uuid}/transactions",
    response_model=TransactionRead,
    status_code=201,
)
async def add_group_transaction(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="The UUID of the group",
        ),
    ],
    transaction_create: TransactionCreate,
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
        raise NotFoundException("Group not found.")

    # Check if user is part of the group
    user_group_exists: bool = await crud_group_user.exists(
        db=db,
        user_uuid=current_user.uuid,
        group_uuid=group_uuid,
    )
    if not user_group_exists:
        raise ForbiddenException()

    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=transaction_create.purchase_category_uuid, is_deleted=False
    )
    if not purchase_category_exists:
        raise NotFoundException("Purchase category not found.")

    # Check if group has the purchase category
    group_purchase_category_exists: bool = (
        await crud_group_purchase_category.exists(
            db=db,
            group_uuid=group_uuid,
            purchase_category_uuid=transaction_create.purchase_category_uuid,
        )
    )
    if not group_purchase_category_exists:
        raise ForbiddenException()
    purchase_category_schema: PurchaseCategorySchema | None = (
        await crud_purchase_categories.get(
            db=db,
            uuid=transaction_create.purchase_category_uuid,
            return_as_model=True,
            schema_to_select=PurchaseCategorySchema,
        )
    )
    if purchase_category_schema is None:
        raise CustomException(detail="This should not happen. Error: 1")

    # Check tags and create if necessary
    tags: list[TagSchema | TagModel] = []
    for tag_name in transaction_create.tag_names:
        group_tag_join_config = JoinConfig(
            model=GroupTagModel,
            join_on=GroupTagModel.tag_id == TagModel.id,
            schema_to_select=BaseModel,
            filters={"group_uuid": group_uuid},
        )
        tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
            db=db,
            tag_name=tag_name.strip(),
            is_deleted=False,
            joins_config=[group_tag_join_config],
            schema_to_select=TagSchema,
        )
        if tag_dict is None:
            tag_create_internal = TagCreateInternal(tag_name=tag_name.strip())
            tag_model: TagModel = await crud_tags.create(
                db=db, object=tag_create_internal
            )
            group_tag_create_internal = GroupTagCreateInternal(
                group_id=group_schema.id,
                group_uuid=group_schema.uuid,
                tag_id=tag_model.id,
                tag_uuid=tag_model.uuid,
            )
            await crud_group_tag.create(db=db, object=group_tag_create_internal)
            tags.append(tag_model)
        else:
            tags.append(TagSchema(**tag_dict))

    # Create transaction
    transaction_create_internal = TransactionCreateInternal(
        **transaction_create.model_dump(exclude={"purchase_category_uuid"}),
        purchase_category_id=purchase_category_schema.id,
        purchase_category_uuid=purchase_category_schema.uuid,
    )
    transaction_model: TransactionModel = await crud_transactions.create(
        db=db, object=transaction_create_internal
    )
    transaction_dict = vars(transaction_model)
    transaction_dict.update(
        {
            "category_name": purchase_category_schema.category_name,
            "tag_names": [tag.tag_name for tag in tags],
        }
    )
    transaction_schema = TransactionRead.model_validate(transaction_dict)

    # Create group transaction
    group_transaction_create_internal = GroupTransactionCreateInternal(
        group_id=group_schema.id,
        group_uuid=group_schema.uuid,
        transaction_id=transaction_model.id,
        transaction_uuid=transaction_model.uuid,
        created_by_user_id=current_user.id,
        created_by_user_uuid=current_user.uuid,
    )
    await crud_group_transactions.create(
        db=db, object=group_transaction_create_internal
    )

    # Create transaction tag links
    for tag in tags:
        transaction_tag_create_internal = TransactionTagCreateInternal(
            transaction_id=transaction_model.id,
            transaction_uuid=transaction_model.uuid,
            tag_id=tag.id,
            tag_uuid=tag.uuid,
        )
        await crud_transaction_tag.create(
            db=db, object=transaction_tag_create_internal
        )

    return transaction_schema


@router.get(
    "/group/{group_uuid}/transactions",
    response_model=PaginatedListResponse[TransactionRead],
)
async def get_group_transactions(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="The UUID of the group",
        ),
    ],
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
    # Check if group exists
    group_schema: GroupSchema | None = await crud_groups.get(
        db=db,
        uuid=group_uuid,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=GroupSchema,
    )
    if group_schema is None:
        raise NotFoundException("Group not found.")

    # Check if user is part of the group
    user_group_exists: bool = await crud_group_user.exists(
        db=db,
        user_uuid=current_user.uuid,
        group_uuid=group_uuid,
    )
    if not user_group_exists:
        raise ForbiddenException()

    # Check if purchase category exists
    purchase_category_schema: PurchaseCategorySchema | None = None
    if purchase_category_uuid is not None:
        purchase_category_exists: bool = await crud_purchase_categories.exists(
            db=db, uuid=purchase_category_uuid, is_deleted=False
        )
        if not purchase_category_exists:
            raise NotFoundException(
                "Purchase category does not exist or has been deleted."
            )

        # Check if user has access to purchase category
        group_purchase_category_join_config = JoinConfig(
            model=GroupPurchaseCategoryModel,
            join_on=(
                GroupPurchaseCategoryModel.purchase_category_id
                == PurchaseCategoryModel.id
            ),
            schema_to_select=BaseModel,
            filters={"group_id": group_schema.id},
        )
        purchase_category_dict: dict[str, Any] | None = (
            await crud_purchase_categories.get_joined(
                db=db,
                uuid=purchase_category_uuid,
                is_deleted=False,
                joins_config=[group_purchase_category_join_config],
                schema_to_select=PurchaseCategorySchema,
            )
        )
        if purchase_category_dict is None:
            raise ForbiddenException()
        purchase_category_schema = PurchaseCategorySchema(
            **purchase_category_dict
        )

    # Check tags
    tags: list[TagSchema] = []
    for tag_name in tag_names:
        group_tag_join_config = JoinConfig(
            model=GroupTagModel,
            join_on=GroupTagModel.tag_id == TagModel.id,
            schema_to_select=BaseModel,
            filters={"group_id": group_schema.id},
        )
        tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
            db=db,
            tag_name=tag_name.strip(),
            is_deleted=False,
            joins_config=[group_tag_join_config],
            schema_to_select=TagSchema,
        )
        if tag_dict is None:
            raise NotFoundException(f"Tag '{tag_name}' not found.")
        tags.append(TagSchema(**tag_dict))

    # Get transactions
    statement = (
        select(TransactionModel)
        .outerjoin(PurchaseCategoryModel)
        .add_columns(PurchaseCategoryModel.category_name)
        .outerjoin(GroupTransactionModel)
        .outerjoin(TransactionTagModel)
        .outerjoin(TagModel)
        .filter(
            GroupTransactionModel.group_id == group_schema.id,
            not_(TransactionModel.is_deleted),
            not_(PurchaseCategoryModel.is_deleted),
            not_(TagModel.is_deleted),
            (
                TagModel.id.in_([tag.id for tag in tags])
                if len(tags) > 0
                else true()
            ),
        )
        .group_by(TransactionModel.id, PurchaseCategoryModel.id)
        .having(func.count(TagModel.id.distinct()) >= len(tags))
        .offset(compute_offset(page=page, items_per_page=items_per_page))
        .limit(items_per_page)
    )
    if purchase_category_schema is not None:
        statement = statement.filter(
            PurchaseCategoryModel.id == purchase_category_schema.id
        )

    db_rows = await db.execute(statement)
    data: list[TransactionRead] = []
    for row in db_rows.mappings().all():
        row_dict = dict(row)
        transaction: dict[str, Any] = vars(row_dict["Transaction"])
        transaction["category_name"] = row_dict["category_name"]

        tags_stmt = (
            select(TagModel)
            .outerjoin(TransactionTagModel)
            .filter(TransactionTagModel.transaction_id == transaction["id"])
        )
        tag_db_rows = await db.execute(tags_stmt)
        tag_data: list[TagRead] = []
        for tag_row in tag_db_rows.mappings().all():
            tag_row_dict = dict(tag_row)
            tag_data.append(TagRead(**vars(tag_row_dict["Tag"])))
        transaction["tag_names"] = [tag.tag_name for tag in tag_data]

        data.append(TransactionRead(**transaction))

    crud_data = {"data": data, "total_count": len(data)}
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )
