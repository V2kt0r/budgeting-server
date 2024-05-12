from typing import Annotated, Any

from fastapi import Depends
from fastcrud import JoinConfig
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....crud.crud_tags import crud_tags
from ....crud.crud_transaction_item import crud_transaction_item
from ....crud.links.crud_transaction_item_tag import crud_transaction_item_tag
from ....crud.links.crud_transaction_transaction_item import (
    crud_transaction_transaction_item,
)
from ....models.links.transaction_item_tag import (
    TransactionItemTag as TransactionItemTagModel,
)
from ....models.links.transaction_transaction_item import (
    TransactionTransactionItem as TransactionTransactionItemModel,
)
from ....models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ....models.tag import Tag as TagModel
from ....models.transaction import Transaction as TransactionModel
from ....models.transaction_item import TransactionItem as TransactionItemModel
from ....schemas.group import Group as GroupSchema
from ....schemas.links.transaction_item_tag import (
    TransactionItemTagCreateInternal,
)
from ....schemas.links.transaction_transaction_item import (
    TransactionTransactionItemCreateInternal,
)
from ....schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ....schemas.purchase_category import PurchaseCategoryBase
from ....schemas.tag import Tag as TagSchema
from ....schemas.transaction import Transaction as TransactionSchema
from ....schemas.transaction_item import (
    TransactionItem as TransactionItemSchema,
)
from ....schemas.transaction_item import (
    TransactionItemCreate,
    TransactionItemCreateInternal,
)
from ....schemas.user import User as UserSchema
from ...dependencies import get_current_user
from .group import get_non_deleted_user_group
from .purchase_category import (
    get_non_deleted_group_purchase_category,
    get_non_deleted_user_purchase_category,
)
from .tag import get_or_create_group_tags, get_or_create_user_tags
from .transaction import (
    get_non_deleted_group_transaction,
    get_non_deleted_user_transaction,
)


async def remove_tags_from_transaction_item(
    transaction_item: TransactionItemSchema | TransactionItemModel,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    try:
        await crud_transaction_item_tag.delete(
            db=db,
            transaction_item_id=transaction_item.id,
            allow_multiple=True,
        )
    except NoResultFound:
        pass
    # TODO: Remove orphaned tags (from user_tags table or group_tags table)


async def add_user_tags_to_transaction_item(
    transaction_item: TransactionItemSchema | TransactionItemModel,
    tag_names: list[str],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    tags: list[TagSchema | TagModel] = await get_or_create_user_tags(
        tag_names=tag_names,
        current_user=current_user,
        db=db,
    )

    for tag in tags:
        await crud_transaction_item_tag.create(
            db=db,
            object=TransactionItemTagCreateInternal(
                transaction_item_id=transaction_item.id,
                transaction_item_uuid=transaction_item.uuid,
                tag_id=tag.id,
                tag_uuid=tag.uuid,
            ),
        )


async def add_group_tags_to_transaction_item(
    transaction_item: TransactionItemSchema | TransactionItemModel,
    tag_names: list[str],
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    tags: list[TagSchema | TagModel] = await get_or_create_group_tags(
        tag_names=tag_names,
        group=group_schema,
        db=db,
    )

    for tag in tags:
        await crud_transaction_item_tag.create(
            db=db,
            object=TransactionItemTagCreateInternal(
                transaction_item_id=transaction_item.id,
                transaction_item_uuid=transaction_item.uuid,
                tag_id=tag.id,
                tag_uuid=tag.uuid,
            ),
        )


async def get_tags_for_transaction_item(
    transaction_item: TransactionItemSchema | TransactionItemModel,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TagSchema]:
    transaction_item_tag_join_config = JoinConfig(
        model=TransactionItemTagModel,
        join_on=TransactionItemTagModel.tag_id == TagModel.id,
        schema_to_select=BaseModel,
        filters={"transaction_item_id": transaction_item.id},
    )
    tag_crud_data: dict[str, Any] = await crud_tags.get_multi_joined(
        db=db,
        is_deleted=False,
        joins_config=[transaction_item_tag_join_config],
        return_as_model=True,
        schema_to_select=TagSchema,
        limit=9999,
    )
    return tag_crud_data["data"]


async def get_tag_names_for_transaction_item(
    transaction_item: TransactionItemSchema | TransactionItemModel,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[str]:
    tags: list[TagSchema] = await get_tags_for_transaction_item(
        transaction_item=transaction_item, db=db
    )
    return [tag.tag_name for tag in tags]


async def remove_user_transaction_items(
    transaction: TransactionSchema | TransactionModel,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    transaction_transaction_item_join_config = JoinConfig(
        model=TransactionTransactionItemModel,
        join_on=(
            TransactionTransactionItemModel.transaction_item_id
            == TransactionItemModel.id
        ),
        schema_to_select=BaseModel,
        filters={"transaction_id": transaction.id},
    )
    crud_data: dict[str, Any] = await crud_transaction_item.get_multi_joined(
        db=db,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=TransactionItemSchema,
        joins_config=[transaction_transaction_item_join_config],
        limit=9999,
    )
    transaction_items = crud_data["data"]
    for transaction_item in transaction_items:
        await remove_tags_from_transaction_item(
            transaction_item=transaction_item, db=db
        )
        await crud_transaction_transaction_item.delete(
            db=db,
            transaction_id=transaction.id,
            transaction_item_id=transaction_item.id,
        )
        await crud_transaction_item.delete(db=db, id=transaction_item.id)
    # TODO: Remove orphaned tags (from user_tags table or group_tags table)


async def remove_group_transaction_items(
    transaction: TransactionSchema | TransactionModel,
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    transaction_transaction_item_join_config = JoinConfig(
        model=TransactionTransactionItemModel,
        join_on=(
            TransactionTransactionItemModel.transaction_item_id
            == TransactionItemModel.id
        ),
        schema_to_select=BaseModel,
        filters={"transaction_id": transaction.id},
    )
    crud_data: dict[str, Any] = await crud_transaction_item.get_multi_joined(
        db=db,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=TransactionItemSchema,
        joins_config=[transaction_transaction_item_join_config],
        limit=9999,
    )
    transaction_items = crud_data["data"]
    for transaction_item in transaction_items:
        await remove_tags_from_transaction_item(
            transaction_item=transaction_item, db=db
        )
        await crud_transaction_transaction_item.delete(
            db=db,
            transaction_id=transaction.id,
            transaction_item_id=transaction_item.id,
        )
        await crud_transaction_item.delete(db=db, id=transaction_item.id)
    # TODO: Remove orphaned tags (from user_tags table or group_tags table)


async def create_user_transaction_items(
    transaction: TransactionSchema | TransactionModel,
    transaction_items: list[TransactionItemCreate],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TransactionItemSchema | TransactionItemModel]:
    result = []
    for transaction_item in transaction_items:
        # Get purchase category
        purchase_category_schema: PurchaseCategorySchema = (
            await get_non_deleted_user_purchase_category(
                purchase_category_uuid=transaction_item.purchase_category_uuid,
                current_user=current_user,
                db=db,
            )
        )

        transaction_item_create_internal: TransactionItemCreateInternal = (
            TransactionItemCreateInternal(
                **transaction_item.model_dump(
                    exclude={"purchase_category_uuid"}
                ),
                purchase_category_id=purchase_category_schema.id,
                purchase_category_uuid=purchase_category_schema.uuid,
            )
        )
        transaction_item_model: TransactionItemModel = (
            await crud_transaction_item.create(
                db=db, object=transaction_item_create_internal
            )
        )
        result.append(transaction_item_model)
        await remove_tags_from_transaction_item(
            transaction_item=transaction_item_model, db=db
        )
        await add_user_tags_to_transaction_item(
            transaction_item=transaction_item_model,
            tag_names=transaction_item.tag_names,
            current_user=current_user,
            db=db,
        )
        await crud_transaction_transaction_item.create(
            db=db,
            object=TransactionTransactionItemCreateInternal(
                transaction_id=transaction.id,
                transaction_uuid=transaction.uuid,
                transaction_item_id=transaction_item_model.id,
                transaction_item_uuid=transaction_item_model.uuid,
            ),
        )

    return result


async def create_group_transaction_items(
    transaction: TransactionSchema | TransactionModel,
    transaction_items: list[TransactionItemCreate],
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TransactionItemSchema | TransactionItemModel]:
    result = []
    for transaction_item in transaction_items:
        # Get purchase category
        purchase_category_schema: PurchaseCategorySchema = (
            await get_non_deleted_group_purchase_category(
                purchase_category_uuid=transaction_item.purchase_category_uuid,
                group=group_schema,
                db=db,
            )
        )

        transaction_item_create_internal: TransactionItemCreateInternal = (
            TransactionItemCreateInternal(
                **transaction_item.model_dump(
                    exclude={"purchase_category_uuid"}
                ),
                purchase_category_id=purchase_category_schema.id,
                purchase_category_uuid=purchase_category_schema.uuid,
            )
        )
        transaction_item_model: TransactionItemModel = (
            await crud_transaction_item.create(
                db=db, object=transaction_item_create_internal
            )
        )
        result.append(transaction_item_model)
        await remove_tags_from_transaction_item(
            transaction_item=transaction_item_model, db=db
        )
        await add_group_tags_to_transaction_item(
            transaction_item=transaction_item_model,
            tag_names=transaction_item.tag_names,
            group_schema=group_schema,
            db=db,
        )
        await crud_transaction_transaction_item.create(
            db=db,
            object=TransactionTransactionItemCreateInternal(
                transaction_id=transaction.id,
                transaction_uuid=transaction.uuid,
                transaction_item_id=transaction_item_model.id,
                transaction_item_uuid=transaction_item_model.uuid,
            ),
        )

    return result


async def get_user_transaction_items(
    transaction: Annotated[
        TransactionSchema | TransactionModel,
        Depends(get_non_deleted_user_transaction),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TransactionItemSchema]:
    transaction_transaction_item_join_config = JoinConfig(
        model=TransactionTransactionItemModel,
        join_on=(
            TransactionTransactionItemModel.transaction_item_id
            == TransactionItemModel.id
        ),
        schema_to_select=BaseModel,
        filters={"transaction_id": transaction.id},
    )
    crud_data: dict[str, Any] = await crud_transaction_item.get_multi_joined(
        db=db,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=TransactionItemSchema,
        joins_config=[transaction_transaction_item_join_config],
        limit=9999,
    )
    return crud_data["data"]


async def get_group_transaction_items(
    transaction: Annotated[
        TransactionSchema | TransactionModel,
        Depends(get_non_deleted_group_transaction),
    ],
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TransactionItemSchema]:
    transaction_transaction_item_join_config = JoinConfig(
        model=TransactionTransactionItemModel,
        join_on=(
            TransactionTransactionItemModel.transaction_item_id
            == TransactionItemModel.id
        ),
        schema_to_select=BaseModel,
        filters={"transaction_id": transaction.id},
    )
    crud_data: dict[str, Any] = await crud_transaction_item.get_multi_joined(
        db=db,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=TransactionItemSchema,
        joins_config=[transaction_transaction_item_join_config],
        limit=9999,
    )
    return crud_data["data"]


async def get_transaction_items_with_data(
    transaction_dict: dict[str, Any],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    transaction_transaction_items_join_config = JoinConfig(
        model=TransactionTransactionItemModel,
        join_on=(
            TransactionTransactionItemModel.transaction_item_id
            == TransactionItemModel.id
        ),
        schema_to_select=BaseModel,
        filters={"transaction_id": transaction_dict["id"]},
    )
    purchase_category_join_config = JoinConfig(
        model=PurchaseCategoryModel,
        join_on=(
            PurchaseCategoryModel.id
            == TransactionItemModel.purchase_category_id
        ),
        schema_to_select=PurchaseCategoryBase,
    )
    transaction_items_crud_data: dict[str, Any] = (
        await crud_transaction_item.get_multi_joined(
            db=db,
            is_deleted=False,
            joins_config=[
                transaction_transaction_items_join_config,
                purchase_category_join_config,
            ],
            return_as_model=False,
            schema_to_select=TransactionItemSchema,
            limit=9999,
        )
    )
    for transaction_item in transaction_items_crud_data["data"]:
        tag_names = await get_tag_names_for_transaction_item(
            transaction_item=TransactionItemSchema(**transaction_item),
            db=db,
        )
        transaction_item["tag_names"] = tag_names
    transaction_dict["transaction_items"] = transaction_items_crud_data["data"]

    return transaction_items_crud_data["data"]
