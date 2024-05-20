from typing import Annotated

from fastapi import Depends
from sqlalchemy import not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
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
from ....schemas.user import User as UserSchema
from ...dependencies import get_current_user
from ..dependencies.group import get_non_deleted_user_group


async def get_user_purchase_categories(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[PurchaseCategoryModel]:
    purchase_categories: list[PurchaseCategoryModel] = []
    statement = (
        select(PurchaseCategoryModel)
        .outerjoin(UserPurchaseCategoryModel)
        .filter(
            UserPurchaseCategoryModel.user_id == current_user.id,
            not_(PurchaseCategoryModel.is_deleted),
        )
    )
    db_rows = await db.execute(statement)
    for row in db_rows.scalars().all():
        purchase_categories.append(row)
    return purchase_categories


async def get_group_purchase_categories(
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[PurchaseCategoryModel]:
    purchase_categories: list[PurchaseCategoryModel] = []
    statement = (
        select(PurchaseCategoryModel)
        .outerjoin(GroupPurchaseCategoryModel)
        .filter(
            GroupPurchaseCategoryModel.group_id == group_schema.id,
            not_(PurchaseCategoryModel.is_deleted),
        )
    )
    db_rows = await db.execute(statement)
    for row in db_rows.scalars().all():
        purchase_categories.append(row)
    return purchase_categories
