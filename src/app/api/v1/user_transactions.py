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
from ...schemas.links.user_tag import UserTagCreateInternal
from ...schemas.links.user_transaction import UserTransactionCreateInternal
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ...schemas.purchase_category import PurchaseCategoryRead
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
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=transaction_create.purchase_category_uuid, is_deleted=False
    )
    if not purchase_category_exists:
        raise NotFoundException("Purchase category  not found.")

    # Check if user has access to purchase category
    user_purchase_category_join_config = JoinConfig(
        model=UserPurchaseCategoryModel,
        join_on=(
            UserPurchaseCategoryModel.purchase_category_id
            == PurchaseCategoryModel.id
        ),
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    purchase_category_dict: dict[str, Any] | None = (
        await crud_purchase_categories.get_joined(
            db=db,
            uuid=transaction_create.purchase_category_uuid,
            is_deleted=False,
            joins_config=[user_purchase_category_join_config],
            schema_to_select=PurchaseCategorySchema,
        )
    )
    if purchase_category_dict is None:
        raise ForbiddenException()
    purchase_category = PurchaseCategorySchema(**purchase_category_dict)

    # Check tags and create if necessary
    tags: list[TagSchema | TagModel] = []
    for tag_name in transaction_create.tag_names:
        user_tag_join_config = JoinConfig(
            model=UserTagModel,
            join_on=UserTagModel.tag_id == TagModel.id,
            schema_to_select=BaseModel,
            filters={"user_id": current_user.id},
        )
        tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
            db=db,
            tag_name=tag_name.strip(),
            is_deleted=False,
            joins_config=[user_tag_join_config],
            schema_to_select=TagSchema,
        )
        if tag_dict is None:
            tag_create_internal = TagCreateInternal(tag_name=tag_name.strip())
            tag_model: TagModel = await crud_tags.create(
                db=db, object=tag_create_internal
            )
            user_tag_create_internal = UserTagCreateInternal(
                user_id=current_user.id,
                user_uuid=current_user.uuid,
                tag_id=tag_model.id,
                tag_uuid=tag_model.uuid,
            )
            await crud_user_tag.create(db=db, object=user_tag_create_internal)
            tags.append(tag_model)
        else:
            tags.append(TagSchema(**tag_dict))

    transaction_create_internal = TransactionCreateInternal(
        **transaction_create.model_dump(exclude={"purchase_category_uuid"}),
        purchase_category_id=purchase_category.id,
        purchase_category_uuid=purchase_category.uuid,
    )
    transaction: TransactionModel = await crud_transactions.create(
        db=db, object=transaction_create_internal
    )
    transaction_dict = vars(transaction)
    transaction_dict.update(
        {
            "category_name": purchase_category.category_name,
            "tag_names": [tag.tag_name for tag in tags],
        }
    )
    transaction_schema = TransactionRead.model_validate(transaction_dict)

    user_transaction_create_internal = UserTransactionCreateInternal(
        user_id=current_user.id,
        user_uuid=current_user.uuid,
        transaction_id=transaction.id,
        transaction_uuid=transaction.uuid,
    )
    await crud_user_transaction.create(
        db=db, object=user_transaction_create_internal
    )

    # Create transaction tag links
    for tag in tags:
        transaction_tag_create_internal = TransactionTagCreateInternal(
            transaction_id=transaction.id,
            transaction_uuid=transaction.uuid,
            tag_id=tag.id,
            tag_uuid=tag.uuid,
        )
        await crud_transaction_tag.create(
            db=db, object=transaction_tag_create_internal
        )

    return transaction_schema


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
        user_purchase_category_join_config = JoinConfig(
            model=UserPurchaseCategoryModel,
            join_on=(
                UserPurchaseCategoryModel.purchase_category_id
                == PurchaseCategoryModel.id
            ),
            schema_to_select=BaseModel,
            filters={"user_id": current_user.id},
        )
        purchase_category_dict: dict[str, Any] | None = (
            await crud_purchase_categories.get_joined(
                db=db,
                uuid=purchase_category_uuid,
                is_deleted=False,
                joins_config=[user_purchase_category_join_config],
                schema_to_select=PurchaseCategorySchema,
            )
        )
        if purchase_category_dict is None:
            raise ForbiddenException()
        purchase_category = PurchaseCategorySchema(**purchase_category_dict)

    # Check tags
    tags: list[TagSchema] = []
    for tag_name in tag_names:
        user_tag_join_config = JoinConfig(
            model=UserTagModel,
            join_on=UserTagModel.tag_id == TagModel.id,
            schema_to_select=BaseModel,
            filters={"user_id": current_user.id},
        )
        tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
            db=db,
            tag_name=tag_name.strip(),
            is_deleted=False,
            joins_config=[user_tag_join_config],
            schema_to_select=TagSchema,
        )
        if tag_dict is None:
            raise NotFoundException(f"Tag '{tag_name}' not found.")
        tags.append(TagSchema(**tag_dict))

    # Get transactions
    # join_configs = []
    # if purchase_category is not None:
    #     purcahse_category_join_config = JoinConfig(
    #         model=PurchaseCategoryModel,
    #         join_on=(
    #             PurchaseCategoryModel.id
    #             == TransactionModel.purchase_category_uuid
    #         ),
    #         schema_to_select=PurchaseCategoryRead,
    #         filters={"uuid": purchase_category.uuid},
    #     )
    #     join_configs.append(purcahse_category_join_config)
    # if tag_names is not None:
    #     join_on_field: Any = None
    #     if len(tags) == 0:
    #         join_on_field = (
    #             TransactionModel.id == TransactionTagModel.transaction_id
    #         )
    #     else:
    #         # TODO: this is not correct, need to fix
    #         join_on_field = and_(
    #             TransactionModel.id == TransactionTagModel.transaction_id,
    #             TransactionTagModel.tag_id.in_([tag.id for tag in tags]),
    #         )
    #     transaction_tag_join_configs = JoinConfig(
    #         model=TransactionTagModel,
    #         join_on=join_on_field,
    #         schema_to_select=BaseModel,
    #     )
    #     join_configs.append(transaction_tag_join_configs)
    # crud_data: dict[str, Any] = await crud_transactions.get_multi_joined(
    #     db=db,
    #     return_as_model=True,
    #     schema_to_select=TransactionRead,
    #     joins_config=join_configs,
    #     offset=compute_offset(page=page, items_per_page=items_per_page),
    #     limit=items_per_page,
    #     is_deleted=False,
    # )
    # for transaction in crud_data["data"]:
    #     transaction_tag_join_config = JoinConfig(
    #         model=TransactionTagModel,
    #         join_on=TransactionTagModel.tag_id == TagModel.id,
    #         schema_to_select=BaseModel,
    #         filters={"transaction_id": transaction.id},
    #     )
    #     tag_crud_data = await crud_tags.get_multi_joined(
    #         db=db,
    #         return_as_model=True,
    #         schema_to_select=TagRead,
    #         joins_config=[transaction_tag_join_config],
    #         limit=9999,
    #         is_deleted=False,
    #     )
    #     transaction["tag_names"] = [
    #         tag.tag_name for tag in tag_crud_data["data"]
    #     ]
    # return paginated_response(
    #     crud_data=crud_data, page=page, items_per_page=items_per_page
    # )

    statement = (
        select(TransactionModel)
        .outerjoin(PurchaseCategoryModel)
        .add_columns(PurchaseCategoryModel.category_name)
        .outerjoin(UserTransactionModel)
        .outerjoin(TransactionTagModel)
        .outerjoin(TagModel)
        .filter(
            UserTransactionModel.user_id == current_user.id,
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
    if purchase_category is not None:
        statement = statement.filter(
            PurchaseCategoryModel.id == purchase_category.id
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


@router.get("/transactions/{transaction_uuid}", response_model=TransactionRead)
async def get_transaction(
    *,
    request: Request,
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the transaction to retrieve",
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Check if transaction exists
    transaction_exists: bool = await crud_transactions.exists(
        db=db, uuid=transaction_uuid, is_deleted=False
    )
    if not transaction_exists:
        raise NotFoundException(
            "Transaction does not exist or has been deleted."
        )

    # Check if user has access to transaction
    user_transaction_join_config = JoinConfig(
        model=UserTransactionModel,
        join_on=UserTransactionModel.transaction_id == TransactionModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    category_join_config = JoinConfig(
        model=PurchaseCategoryModel,
        join_on=(
            PurchaseCategoryModel.id == TransactionModel.purchase_category_id
        ),
        schema_to_select=PurchaseCategoryRead,
    )
    transaction_dict: dict[str, Any] | None = (
        await crud_transactions.get_joined(
            db=db,
            uuid=transaction_uuid,
            is_deleted=False,
            joins_config=[user_transaction_join_config, category_join_config],
            schema_to_select=TransactionRead,
        )
    )
    if transaction_dict is None:
        raise ForbiddenException()

    # Get tags
    transaction_tag_join_config = JoinConfig(
        model=TransactionTagModel,
        join_on=TransactionTagModel.tag_id == TagModel.id,
        schema_to_select=BaseModel,
        filters={"transaction_uuid": transaction_dict["uuid"]},
    )
    tag_crud_data: dict[str, Any] = await crud_tags.get_multi_joined(
        db=db,
        return_as_model=True,
        schema_to_select=TagRead,
        joins_config=[transaction_tag_join_config],
        limit=9999,
        is_deleted=False,
    )
    transaction_dict["tag_names"] = [
        tag.tag_name for tag in tag_crud_data["data"]
    ]
    return TransactionRead(**transaction_dict)


@router.put(
    "/transactions/{transaction_uuid}",
    response_model=Message,
)
async def update_transaction(
    *,
    request: Request,
    transaction_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the transaction to update",
        ),
    ],
    transaction_update: Annotated[TransactionUpdate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if transaction exists
    transaction_exists: bool = await crud_transactions.exists(
        db=db, uuid=transaction_uuid, is_deleted=False
    )
    if not transaction_exists:
        raise NotFoundException(
            "Transaction does not exist or has been deleted."
        )

    # Check if user has access to transaction
    user_transaction_join_config = JoinConfig(
        model=UserTransactionModel,
        join_on=UserTransactionModel.transaction_id == TransactionModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    category_join_config = JoinConfig(
        model=PurchaseCategoryModel,
        join_on=(
            PurchaseCategoryModel.id == TransactionModel.purchase_category_id
        ),
        schema_to_select=PurchaseCategoryRead,
    )
    transaction_dict: dict[str, Any] | None = (
        await crud_transactions.get_joined(
            db=db,
            uuid=transaction_uuid,
            is_deleted=False,
            joins_config=[user_transaction_join_config, category_join_config],
            schema_to_select=TransactionSchema,
        )
    )
    if transaction_dict is None:
        raise ForbiddenException()
    transaction: TransactionSchema = TransactionSchema(**transaction_dict)

    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db,
        uuid=transaction_update.purchase_category_uuid,
        is_deleted=False,
    )
    if not purchase_category_exists:
        raise NotFoundException("Purchase category does not exist.")

    # Check if user has access to purchase category
    user_purchase_category_join_config = JoinConfig(
        model=UserPurchaseCategoryModel,
        join_on=(
            UserPurchaseCategoryModel.purchase_category_id
            == PurchaseCategoryModel.id
        ),
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    purchase_category_dict: dict[str, Any] | None = (
        await crud_purchase_categories.get_joined(
            db=db,
            uuid=transaction_update.purchase_category_uuid,
            is_deleted=False,
            joins_config=[user_purchase_category_join_config],
            schema_to_select=PurchaseCategorySchema,
        )
    )
    if purchase_category_dict is None:
        raise ForbiddenException()
    purchase_category = PurchaseCategorySchema(**purchase_category_dict)

    # Remove old tags
    await crud_transaction_tag.delete(
        db=db, transaction_uuid=transaction_uuid, allow_multiple=True
    )

    # Check tags and create if necessary
    tags: list[TagSchema | TagModel] = []
    for tag_name in transaction_update.tag_names:
        user_tag_join_config = JoinConfig(
            model=UserTagModel,
            join_on=UserTagModel.tag_id == TagModel.id,
            schema_to_select=BaseModel,
            filters={"user_id": current_user.id},
        )
        tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
            db=db,
            tag_name=tag_name.strip(),
            is_deleted=False,
            joins_config=[user_tag_join_config],
            schema_to_select=TagSchema,
        )
        if tag_dict is None:
            tag_create_internal = TagCreateInternal(tag_name=tag_name.strip())
            tag_model: TagModel = await crud_tags.create(
                db=db, object=tag_create_internal
            )
            user_tag_create_internal = UserTagCreateInternal(
                user_id=current_user.id,
                user_uuid=current_user.uuid,
                tag_id=tag_model.id,
                tag_uuid=tag_model.uuid,
            )
            await crud_user_tag.create(db=db, object=user_tag_create_internal)
            tags.append(tag_model)
        else:
            tags.append(TagSchema(**tag_dict))

    # Update transaction
    transaction_update_internal = TransactionUpdateInternal(
        **transaction_update.model_dump(exclude={"purchase_category_uuid"}),
        purchase_category_id=purchase_category.id,
        purchase_category_uuid=purchase_category.uuid,
    )
    await crud_transactions.update(
        db=db,
        uuid=transaction_uuid,
        object=transaction_update_internal.model_dump(),
    )
    for tag in tags:
        transaction_tag_create_internal = TransactionTagCreateInternal(
            transaction_id=transaction.id,
            transaction_uuid=transaction.uuid,
            tag_id=tag.id,
            tag_uuid=tag.uuid,
        )
        await crud_transaction_tag.create(
            db=db, object=transaction_tag_create_internal
        )
    # TODO: clean up tags that are no longer in use
    return Message(message="Transaction updated successfully.")
