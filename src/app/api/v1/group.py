import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Path, Query, Request
from fastcrud import JoinConfig
from fastcrud.paginated import PaginatedListResponse, paginated_response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    ForbiddenException,
    NotFoundException,
)
from ...core.schemas.utils import Message
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
    GroupUpdate,
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


@router.get("/group/{group_uuid}", response_model=GroupReadWithUserRole)
async def get_group(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the group to retrieve",
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(
        db=db, uuid=group_uuid, is_deleted=False
    )
    if not group_exists:
        raise NotFoundException(
            "The group does not exist or has been deleted from the system."
        )

    # Check if user is part of the group
    group_user_join_config = JoinConfig(
        model=GroupUserModel,
        join_on=GroupUserModel.group_id == GroupModel.id,
        schema_to_select=GroupUserBase,
        filters={"user_id": current_user.id},
    )
    group_dict: dict[str, Any] | None = await crud_groups.get_joined(
        db=db,
        uuid=group_uuid,
        is_deleted=False,
        joins_config=[group_user_join_config],
        return_as_model=True,
        schema_to_select=GroupReadWithUserRole,
    )
    if group_dict is None:
        raise ForbiddenException()

    return group_dict


@router.put("/group/{group_uuid}", response_model=Message)
async def update_group(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the group to update",
        ),
    ],
    group_update: Annotated[GroupUpdate, Body()],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(
        db=db, uuid=group_uuid, is_deleted=False
    )
    if not group_exists:
        raise NotFoundException(
            "The group does not exist or has been deleted from the system."
        )

    # Check if user has permission to update the group
    group_user_join_config = JoinConfig(
        model=GroupUserModel,
        join_on=GroupUserModel.group_id == GroupModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id, "user_role": UserRole.ADMIN},
    )
    group_dict: dict[str, Any] | None = await crud_groups.get_joined(
        db=db,
        uuid=group_uuid,
        is_deleted=False,
        joins_config=[group_user_join_config],
        return_as_model=True,
        schema_to_select=GroupRead,
    )
    if group_dict is None:
        raise ForbiddenException()

    await crud_groups.update(db=db, uuid=group_uuid, object=group_update)
    return Message(message="Group updated successfully")


@router.delete("/group/{group_uuid}", response_model=Message)
async def delete_group(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the group to delete",
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(db=db, uuid=group_uuid)
    if not group_exists:
        raise NotFoundException("The group does not exist.")

    # Check if user has permission to delete the group
    group_user_join_config = JoinConfig(
        model=GroupUserModel,
        join_on=GroupUserModel.group_id == GroupModel.id,
        schema_to_select=GroupUserBase,
        filters={"user_id": current_user.id, "user_role": UserRole.ADMIN},
    )
    group_dict: dict[str, Any] | None = await crud_groups.get_joined(
        db=db,
        uuid=group_uuid,
        joins_config=[group_user_join_config],
        return_as_model=True,
        schema_to_select=GroupRead,
    )
    if group_dict is None:
        raise ForbiddenException()

    await crud_groups.delete(db=db, uuid=group_uuid)
    return Message(message="Group deleted successfully")
