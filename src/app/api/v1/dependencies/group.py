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
from ....crud.crud_groups import crud_groups
from ....models.group import Group as GroupModel
from ....models.links.group_user import GroupUser as GroupUserModel
from ....schemas.group import Group as GroupSchema
from ....schemas.user import User as UserSchema
from ...dependencies import get_current_user


async def get_existing_non_deleted_group_uuid(
    group_uuid: uuid_pkg.UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(
        db=db, uuid=group_uuid, is_deleted=False
    )
    if not group_exists:
        raise NotFoundException("Group not found.")

    return group_uuid


async def get_existing_group_uuid(
    group_uuid: uuid_pkg.UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> uuid_pkg.UUID:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(db=db, uuid=group_uuid)
    if not group_exists:
        raise NotFoundException("Group not found.")

    return group_uuid


async def _get_user_group(
    group_uuid: uuid_pkg.UUID,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> GroupSchema:
    # Check if user has access to group
    user_group_join_config = JoinConfig(
        model=GroupUserModel,
        join_on=GroupUserModel.group_id == GroupModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    group_dict: dict[str, Any] | None = await crud_groups.get_joined(
        db=db,
        uuid=group_uuid,
        joins_config=[user_group_join_config],
        schema_to_select=GroupSchema,
    )
    if group_dict is None:
        raise ForbiddenException("User does not have access to group.")

    group_schema = GroupSchema.model_validate(group_dict)
    return group_schema


async def get_non_deleted_user_group(
    group_uuid: Annotated[
        uuid_pkg.UUID, Depends(get_existing_non_deleted_group_uuid)
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> GroupSchema:
    return await _get_user_group(
        group_uuid=group_uuid, current_user=current_user, db=db
    )


async def get_user_group(
    group_uuid: Annotated[uuid_pkg.UUID, Depends(get_existing_group_uuid)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> GroupSchema:
    return await _get_user_group(
        group_uuid=group_uuid, current_user=current_user, db=db
    )
