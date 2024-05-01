from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Query, Request
from fastcrud import JoinConfig
from fastcrud.paginated import PaginatedListResponse, paginated_response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_groups import crud_groups
from ...crud.links.crud_group_user import crud_group_user
from ...models.group import Group as GroupModel
from ...models.links.group_user import GroupUser as GroupUserModel
from ...models.links.group_user import UserRole
from ...schemas.group import (
    GroupCreate,
    GroupCreateInternal,
    GroupRead,
    GroupReadWithUserRole,
)
from ...schemas.links.group_user import GroupUserBase, GroupUserCreateInternal
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user

router = APIRouter(tags=["group"])


@router.post("/group", response_model=GroupRead, status_code=201)
async def create_group(
    *,
    request: Request,
    group_create: Annotated[GroupCreate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    group_model: GroupModel = await crud_groups.create(
        db=db, object=GroupCreateInternal(**group_create.model_dump())
    )
    await crud_group_user.create(
        db=db,
        object=GroupUserCreateInternal(
            group_id=group_model.id,
            group_uuid=group_model.uuid,
            user_id=current_user.id,
            user_uuid=current_user.uuid,
            user_role=UserRole.ADMIN,
        ),
    )
    return group_model


@router.get(
    "/group", response_model=PaginatedListResponse[GroupReadWithUserRole]
)
async def get_groups(
    *,
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Any:
    group_user_join_config = JoinConfig(
        model=GroupUserModel,
        join_on=GroupModel.id == GroupUserModel.group_id,
        schema_to_select=GroupUserBase,
        filters={"user_id": current_user.id},
    )
    crud_data: dict[str, Any] = await crud_groups.get_multi_joined(
        db=db,
        is_deleted=False,
        joins_config=[group_user_join_config],
        return_as_model=True,
        schema_to_select=GroupReadWithUserRole,
    )
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )
