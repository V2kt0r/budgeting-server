from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from sqlalchemy import func, not_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...models.links.transaction_item_tag import (
    TransactionItemTag as TransactionItemTagModel,
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
from ...models.tag import Tag as TagModel
from ...models.transaction import Transaction as TransactionModel
from ...models.transaction_item import TransactionItem as TransactionItemModel
from ...schemas.purchase_category import (
    PurchaseCategory as PurchaseCategorySchema,
)
from ...schemas.tag import Tag as TagSchema
from ...schemas.tag import TagRead
from ...schemas.transaction_item import (
    TransactionItemRead,
    TransactionItemReadWithTransactionData,
)
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user
from .dependencies.purchase_category import (
    get_optional_non_deleted_user_purchase_category,
)
from .dependencies.tag import get_non_deleted_user_tags

router = APIRouter(tags=["User Transaction Items"])


@router.get(
    "/transaction-items",
    response_model=PaginatedListResponse[
        TransactionItemReadWithTransactionData
    ],
)
async def get_user_transaction_items(
    *,
    before: datetime | None = Query(
        default=None,
        description="Get transactions before this date",
        examples=[datetime.now(UTC)],
    ),
    after: datetime | None = Query(
        default=None,
        description="Get transactions after this date",
        examples=[datetime.now(UTC) - timedelta(days=7)],
    ),
    tag_schemas: Annotated[list[TagSchema], Depends(get_non_deleted_user_tags)],
    purchase_category_schema: Annotated[
        PurchaseCategorySchema,
        Depends(get_optional_non_deleted_user_purchase_category),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Any:
    statement = (
        select(TransactionItemModel)
        .outerjoin(PurchaseCategoryModel)
        .add_columns(PurchaseCategoryModel.category_name)
        .outerjoin(TransactionTransactionItemModel)
        .outerjoin(TransactionModel)
        .add_columns(TransactionModel.uuid, TransactionModel.timestamp)
        .outerjoin(UserTransactionModel)
        .outerjoin(TransactionItemTagModel)
        .outerjoin(TagModel)
        .filter(
            UserTransactionModel.user_id == current_user.id,
            not_(TransactionModel.is_deleted),
            not_(TransactionItemModel.is_deleted),
            not_(TagModel.is_deleted),
            not_(PurchaseCategoryModel.is_deleted),
            (
                TagModel.id.in_([tag.id for tag in tag_schemas])
                if len(tag_schemas) > 0
                else true()
            ),
        )
        .group_by(
            TransactionItemModel.id,
            PurchaseCategoryModel.id,
            TransactionModel.id,
        )
        .having(func.count(TagModel.id.distinct()) >= len(tag_schemas))
        .offset(compute_offset(page=page, items_per_page=items_per_page))
        .limit(items_per_page)
    )
    if before:
        statement = statement.filter(TransactionModel.timestamp < before)
    if after:
        statement = statement.filter(TransactionModel.timestamp > after)
    if purchase_category_schema:
        statement = statement.filter(
            PurchaseCategoryModel.id == purchase_category_schema.id
        )

    db_rows = await db.execute(statement)
    data: list[TransactionItemRead] = []
    for row in db_rows.mappings().all():
        row_dict = dict(row)
        transaction_item_dict: dict[str, Any] = vars(
            row_dict["TransactionItem"]
        )
        transaction_item_dict["category_name"] = row_dict["category_name"]
        transaction_item_dict["transaction_uuid"] = row_dict["uuid"]
        transaction_item_dict["timestamp"] = row_dict["timestamp"]

        tags_statement = (
            select(TagModel)
            .outerjoin(TransactionItemTagModel)
            .filter(
                TransactionItemTagModel.transaction_item_id
                == transaction_item_dict["id"]
            )
        )
        tags_db_rows = await db.execute(tags_statement)
        tag_data: list[TagRead] = []
        for tag_row in tags_db_rows.mappings().all():
            tag_row_dict: dict[str, Any] = dict(tag_row)
            tag_data.append(TagRead(**vars(tag_row_dict["Tag"])))
        transaction_item_dict["tag_names"] = [tag.tag_name for tag in tag_data]

        data.append(
            TransactionItemReadWithTransactionData.model_validate(
                transaction_item_dict
            )
        )

    crud_data = {"data": data, "total_count": len(data)}
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )
