import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    Path,
    Query,
    Request,
    Response,
)
from fastcrud import JoinConfig
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from pydantic import BaseModel, Field
from sqlalchemy import func, not_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    CustomException,
    ForbiddenException,
    NotFoundException,
)
from ...core.schemas.utils import Message
from ...crud.crud_groups import crud_groups
from ...crud.crud_purchase_categories import crud_purchase_categories
from ...crud.crud_tags import crud_tags
from ...crud.crud_transactions import crud_transactions
from ...crud.crud_users import crud_users
from ...crud.links.crud_group_purchase_category import (
    crud_group_purchase_category,
)
from ...crud.links.crud_group_tag import crud_group_tag
from ...crud.links.crud_group_transaction import crud_group_transactions
from ...crud.links.crud_group_user import crud_group_user
from ...crud.links.crud_transaction_tag import crud_transaction_tag
from ...models.links.group_purchase_category import (
    GroupPurchaseCategory as GroupPurchaseCategoryModel,
)
from ...models.links.group_tag import GroupTag as GroupTagModel
from ...models.links.group_transaction import (
    GroupTransaction as GroupTransactionModel,
)
from ...models.links.group_user import UserRole
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
from ...schemas.links.group_transaction import (
    GroupTransactionCreateInternal,
)
from ...schemas.links.group_user import (
    GroupUserCreateInternal,
    GroupUserUpdateInternal,
)
from ...schemas.links.transaction_tag import TransactionTagCreateInternal
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

router = APIRouter(tags=["Group Members"])


@router.post(
    "/group/{group_uuid}/users/{user_uuid}",
    response_model=Message,
    status_code=201,
)
async def add_group_user(
    *,
    request: Request,
    response: Response,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the group",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    user_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the user",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    user_role: UserRole = Query(
        description="The role of the user in the group",
        examples=[role for role in UserRole],
        default=UserRole.MEMBER,
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if group exists
    group_schema: GroupSchema | None = await crud_groups.get(
        db=db,
        uuid=group_uuid,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=GroupSchema,
    )
    if group_schema is None:
        raise NotFoundException("The group with this UUID does not exist")

    # Check if user is in the group and is an admin
    user_has_permission: bool = await crud_group_user.exists(
        db=db,
        group_uuid=group_uuid,
        user_uuid=current_user.uuid,
        user_role=UserRole.ADMIN,
    )
    if not user_has_permission:
        raise ForbiddenException()

    # Check if user exists
    user_schema: UserSchema | None = await crud_users.get(
        db=db,
        uuid=user_uuid,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=UserSchema,
    )
    if user_schema is None:
        raise NotFoundException("The user with this UUID does not exist")

    # Check if user is already in the group
    user_in_group: bool = await crud_group_user.exists(
        db=db, group_uuid=group_uuid, user_uuid=user_uuid
    )
    if user_in_group:
        response.status_code = 200
        return Message(message="User is already in the group")

    # Add user to group
    await crud_group_user.create(
        db=db,
        object=GroupUserCreateInternal(
            group_id=group_schema.id,
            group_uuid=group_uuid,
            user_id=user_schema.id,
            user_uuid=user_schema.uuid,
            user_role=user_role,
        ),
    )
    return Message(message="User added to group")


@router.put(
    "/group/{group_uuid}/users/{user_uuid}",
    response_model=Message,
    status_code=200,
)
async def change_group_user_role(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the group",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    user_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the user",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    user_role: Annotated[
        UserRole,
        Query(
            description="The role of the user in the group",
            examples=[role for role in UserRole],
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if group exists
    group_schema: GroupSchema | None = await crud_groups.get(
        db=db,
        uuid=group_uuid,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=GroupSchema,
    )
    if group_schema is None:
        raise NotFoundException("The group with this UUID does not exist")

    # Check if user is in the group and is an admin
    user_has_permission: bool = await crud_group_user.exists(
        db=db,
        group_uuid=group_uuid,
        user_uuid=current_user.uuid,
        user_role=UserRole.ADMIN,
    )
    if not user_has_permission:
        raise ForbiddenException()

    # Check if user exists
    user_schema: UserSchema | None = await crud_users.get(
        db=db,
        uuid=user_uuid,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=UserSchema,
    )
    if user_schema is None:
        raise NotFoundException("The user with this UUID does not exist")

    # Check if user is in the group
    user_in_group: bool = await crud_group_user.exists(
        db=db, group_uuid=group_uuid, user_uuid=user_uuid
    )
    if not user_in_group:
        raise NotFoundException("The user is not in the group")

    # Change user role
    await crud_group_user.update(
        db=db,
        group_uuid=group_uuid,
        user_uuid=user_uuid,
        object=GroupUserUpdateInternal(user_role=user_role),
    )
    return Message(message="User role updated")
