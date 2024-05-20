from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...models.links.transaction_transaction_item import (
    TransactionTransactionItem as TransactionTransactionItemModel,
)
from ...models.links.user_transaction import (
    UserTransaction as UserTransactionModel,
)
from ...models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ...models.transaction import Transaction as TransactionModel
from ...models.transaction_item import TransactionItem as TransactionItemModel
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
    PurchaseCategoryRead,
)
from ...schemas.statistics import (
    PurchaseCategoryStatistics,
    PurchaseCategoryStatisticsItem,
)
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user
from .dependencies.statistics import get_user_purchase_categories

router = APIRouter(tags=["User Statistics"])


@router.get(
    "/stats/by-purchase-category", response_model=PurchaseCategoryStatistics
)
async def get_purchase_category_statistics(
    request: Request,
    purchase_categories: Annotated[
        list[PurchaseCategoryModel | PurchaseCategorySchema],
        Depends(get_user_purchase_categories),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    total_count: int = 0
    total: float = 0
    items: list[PurchaseCategoryStatisticsItem] = []

    for purchase_category in purchase_categories:
        statement = (
            select(
                func.sum(TransactionItemModel.amount).label("total"),
                func.count(TransactionItemModel.id).label("item_count"),
            )
            .select_from(TransactionItemModel)
            .outerjoin(PurchaseCategoryModel)
            .outerjoin(TransactionTransactionItemModel)
            .outerjoin(TransactionModel)
            .outerjoin(UserTransactionModel)
            .filter(
                UserTransactionModel.user_id == current_user.id,
                PurchaseCategoryModel.id == purchase_category.id,
                not_(TransactionModel.is_deleted),
                not_(TransactionItemModel.is_deleted),
                not_(PurchaseCategoryModel.is_deleted),
            )
            .group_by(PurchaseCategoryModel.id)
        )
        result = await db.execute(statement)
        row = result.fetchone()
        if row:
            category_total = row.total or 0
            category_count = row.item_count or 0
        else:
            category_total = 0
            category_count = 0

        total_count += category_count
        total += category_total
        items.append(
            PurchaseCategoryStatisticsItem(
                purchase_category=PurchaseCategoryRead(
                    **vars(purchase_category)
                ),
                item_count=category_count,
                total=category_total,
            )
        )

    return PurchaseCategoryStatistics(
        total=total, item_count=total_count, items=items
    )
