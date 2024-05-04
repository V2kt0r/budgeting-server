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
from ...crud.links.crud_user_purchase_category import (
    crud_user_purchase_category,
)
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

router = APIRouter(tags=["User Purchase Category"])


@router.post(
    "/purchase-category", response_model=PurchaseCategoryRead, status_code=201
)
async def create_purchase_category(
    *,
    request: Request,
    purchase_category_create: Annotated[PurchaseCategoryCreate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Create the purchase category
    purchase_category_model: PurchaseCategoryModel = (
        await crud_purchase_categories.create(
            db=db,
            object=PurchaseCategoryCreateInternal.model_validate(
                purchase_category_create.model_dump()
            ),
        )
    )

    # Create the user purchase category link
    user_purchase_category_model: UserPurchaseCategoryModel = (
        await crud_user_purchase_category.create(
            db=db,
            object=UserPurchaseCategoryCreateInternal(
                user_id=current_user.id,
                user_uuid=current_user.uuid,
                purchase_category_id=purchase_category_model.id,
                purchase_category_uuid=purchase_category_model.uuid,
            ),
        )
    )

    return purchase_category_model
