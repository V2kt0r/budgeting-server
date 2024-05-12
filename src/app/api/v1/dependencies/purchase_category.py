import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import Depends
from fastcrud import JoinConfig
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import (
    ForbiddenException,
    NotFoundException,
)
from ....crud.crud_purchase_categories import crud_purchase_categories
from ....models.links.group_purchase_category import (
    GroupPurchaseCategory as GroupPurchaseCategoryModel,
)
from ....models.links.user_purchase_category import (
    UserPurchaseCategory as UserPurchaseCategoryModel,
)
from ....models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ....schemas.group import Group as GroupSchema
from ....schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ....schemas.user import User as UserSchema
from ...dependencies import get_current_user
from ..dependencies.group import get_non_deleted_user_group


async def get_existing_non_deleted_purchase_category_uuid(
    purchase_category_uuid: uuid_pkg.UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID:
    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=purchase_category_uuid, is_deleted=False
    )
    if not purchase_category_exists:
        raise NotFoundException("Purchase category not found.")

    return purchase_category_uuid


async def get_existing_non_deleted_optional_purchase_category_uuid(
    *,
    purchase_category_uuid: uuid_pkg.UUID | None = None,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID | None:
    if purchase_category_uuid is None:
        return None
    return await get_existing_non_deleted_purchase_category_uuid(
        purchase_category_uuid=purchase_category_uuid,
        db=db,
    )


async def get_existing_purchase_category_uuid(
    purchase_category_uuid: uuid_pkg.UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID:
    # Check if purchase category exists
    purchase_category_exists: bool = await crud_purchase_categories.exists(
        db=db, uuid=purchase_category_uuid
    )
    if not purchase_category_exists:
        raise NotFoundException("Purchase category not found.")

    return purchase_category_uuid


async def get_existing_optional_purchase_category_uuid(
    *,
    purchase_category_uuid: uuid_pkg.UUID | None = None,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID | None:
    if purchase_category_uuid is None:
        return None
    return await get_existing_purchase_category_uuid(
        purchase_category_uuid=purchase_category_uuid,
        db=db,
    )


async def _get_user_purchase_category(
    purchase_category_uuid: uuid_pkg.UUID,
    current_user: UserSchema,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema:
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
            joins_config=[user_purchase_category_join_config],
            schema_to_select=PurchaseCategorySchema,
        )
    )
    if purchase_category_dict is None:
        raise ForbiddenException(
            "User does not have access to purchase category."
        )

    purchase_category_schema = PurchaseCategorySchema.model_validate(
        purchase_category_dict
    )

    return purchase_category_schema


async def _get_group_purchase_category(
    purchase_category_uuid: uuid_pkg.UUID,
    group: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema:
    # Check if group has access to purchase category
    group_purchase_category_join_config = JoinConfig(
        model=GroupPurchaseCategoryModel,
        join_on=(
            GroupPurchaseCategoryModel.purchase_category_id
            == PurchaseCategoryModel.id
        ),
        schema_to_select=BaseModel,
        filters={"group_id": group.id},
    )
    purchase_category_dict: dict[str, Any] | None = (
        await crud_purchase_categories.get_joined(
            db=db,
            uuid=purchase_category_uuid,
            joins_config=[group_purchase_category_join_config],
            schema_to_select=PurchaseCategorySchema,
        )
    )
    if purchase_category_dict is None:
        raise ForbiddenException(
            "Group does not have access to purchase category."
        )

    purchase_category_schema = PurchaseCategorySchema.model_validate(
        purchase_category_dict
    )

    return purchase_category_schema


async def get_non_deleted_user_purchase_category(
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID, Depends(get_existing_non_deleted_purchase_category_uuid)
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema:
    return await _get_user_purchase_category(
        purchase_category_uuid=purchase_category_uuid,
        current_user=current_user,
        db=db,
    )


async def get_non_deleted_group_purchase_category(
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID, Depends(get_existing_non_deleted_purchase_category_uuid)
    ],
    group: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema:
    return await _get_group_purchase_category(
        purchase_category_uuid=purchase_category_uuid,
        group=group,
        db=db,
    )


async def get_optional_non_deleted_user_purchase_category(
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID | None,
        Depends(get_existing_non_deleted_optional_purchase_category_uuid),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema | None:
    if purchase_category_uuid is None:
        return None
    return await _get_user_purchase_category(
        purchase_category_uuid=purchase_category_uuid,
        current_user=current_user,
        db=db,
    )


async def get_optional_non_deleted_group_purchase_category(
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID | None,
        Depends(get_existing_non_deleted_optional_purchase_category_uuid),
    ],
    group: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema | None:
    if purchase_category_uuid is None:
        return None
    return await _get_group_purchase_category(
        purchase_category_uuid=purchase_category_uuid,
        group=group,
        db=db,
    )


async def get_user_purchase_category(
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID, Depends(get_existing_purchase_category_uuid)
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema:
    return await _get_user_purchase_category(
        purchase_category_uuid=purchase_category_uuid,
        current_user=current_user,
        db=db,
    )


async def get_optional_user_purchase_category(
    purchase_category_uuid: Annotated[
        uuid_pkg.UUID | None,
        Depends(get_existing_optional_purchase_category_uuid),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PurchaseCategorySchema | None:
    if purchase_category_uuid is None:
        return None
    return await _get_user_purchase_category(
        purchase_category_uuid=purchase_category_uuid,
        current_user=current_user,
        db=db,
    )
