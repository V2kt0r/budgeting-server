from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...models.links.group_transaction import (
    GroupTransaction as GroupTransactionModel,
)
from ...models.links.transaction_transaction_item import (
    TransactionTransactionItem as TransactionTransactionItemModel,
)
from ...models.links.user_transaction import (
    UserTransaction as UserTransactionModel,
)
from ...models.purchase_category import (
    PurchaseCategory as PurchaseCategoryModel,
)
from ...models.transaction import Currency, Transaction as TransactionModel
from ...models.transaction_item import TransactionItem as TransactionItemModel
from ...schemas.group import Group as GroupSchema, GroupRead
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ...schemas.purchase_category import PurchaseCategoryRead
from ...schemas.statistics import (
    GroupPurchaseCategoryStatistics,
    PurchaseCategoryStatistics,
    PurchaseCategoryStatisticsItem,
)
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user
from .dependencies.group import get_non_deleted_user_group
from .dependencies.statistics import (
    get_group_purchase_categories,
    get_user_purchase_categories,
)

router = APIRouter(tags=["User Statistics"])


@router.get(
    "/stats/by-purchase-category", response_model=PurchaseCategoryStatistics
)
async def get_purchase_category_statistics(
    *,
    request: Request,
    purchase_categories: Annotated[
        list[PurchaseCategoryModel | PurchaseCategorySchema],
        Depends(get_user_purchase_categories),
    ],
    currency: Currency = Query(
        default=Currency.HUF,
        description="Currency to use for the statistics",
        examples=[currency for currency in Currency],
    ),
    before: datetime | None = Query(
        default=None,
        description="Get transactions before this date",
        examples=[datetime.now(UTC)],
    ),
    after: datetime | None = Query(
        default=None,
        description="Get transactions after this date",
        examples=[
            datetime.now(UTC) - timedelta(days=7),
            datetime.now(UTC) - timedelta(days=30),
            datetime.now(UTC) - timedelta(days=365),
        ],
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
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
                TransactionModel.currency == currency,
            )
            .group_by(PurchaseCategoryModel.id)
        )

        if before:
            statement = statement.filter(TransactionModel.timestamp < before)
        if after:
            statement = statement.filter(TransactionModel.timestamp > after)

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


@router.get(
    "/group/{group_uuid}/stats/by-purchase-category",
    response_model=PurchaseCategoryStatistics,
)
async def get_group_purchase_category_statistics(
    *,
    request: Request,
    group_schema: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    purchase_categories: Annotated[
        list[PurchaseCategoryModel | PurchaseCategorySchema],
        Depends(get_group_purchase_categories),
    ],
    currency: Currency = Query(
        default=Currency.HUF,
        description="Currency to use for the statistics",
        examples=[currency for currency in Currency],
    ),
    before: datetime | None = Query(
        default=None,
        description="Get transactions before this date",
        examples=[datetime.now(UTC)],
    ),
    after: datetime | None = Query(
        default=None,
        description="Get transactions after this date",
        examples=[
            datetime.now(UTC) - timedelta(days=7),
            datetime.now(UTC) - timedelta(days=30),
            datetime.now(UTC) - timedelta(days=365),
        ],
    ),
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
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
            .outerjoin(GroupTransactionModel)
            .filter(
                GroupTransactionModel.group_id == group_schema.id,
                PurchaseCategoryModel.id == purchase_category.id,
                not_(TransactionModel.is_deleted),
                not_(TransactionItemModel.is_deleted),
                not_(PurchaseCategoryModel.is_deleted),
                TransactionModel.currency == currency,
            )
            .group_by(PurchaseCategoryModel.id)
        )

        if before:
            statement = statement.filter(TransactionModel.timestamp < before)
        if after:
            statement = statement.filter(TransactionModel.timestamp > after)

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

    return GroupPurchaseCategoryStatistics(
        total=total,
        item_count=total_count,
        items=items,
        group=GroupRead(**group_schema.model_dump()),
    )
