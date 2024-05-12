from typing import Annotated, Any

from fastapi import Depends, Query
from fastcrud import JoinConfig
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import NotFoundException
from ....crud.crud_tags import crud_tags
from ....crud.links.crud_group_tag import crud_group_tag
from ....crud.links.crud_user_tag import crud_user_tag
from ....models.links.group_tag import GroupTag as GroupTagModel
from ....models.links.user_tag import UserTag as UserTagModel
from ....models.tag import Tag as TagModel
from ....schemas.group import Group as GroupSchema
from ....schemas.links.group_tag import GroupTagCreateInternal
from ....schemas.links.user_tag import UserTagCreateInternal
from ....schemas.tag import Tag as TagSchema
from ....schemas.tag import TagCreateInternal
from ....schemas.user import User as UserSchema
from ...dependencies import get_current_user
from .group import get_non_deleted_user_group


async def _get_user_tag_dict(
    tag_name: str,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any] | None:
    user_tag_join_config = JoinConfig(
        model=UserTagModel,
        join_on=UserTagModel.tag_id == TagModel.id,
        schema_to_select=BaseModel,
        filters={"user_id": current_user.id},
    )
    tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
        db=db,
        tag_name=tag_name.strip(),
        is_deleted=False,
        joins_config=[user_tag_join_config],
        schema_to_select=TagSchema,
    )
    return tag_dict


async def _get_group_tag_dict(
    tag_name: str,
    group: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any] | None:
    group_tag_join_config = JoinConfig(
        model=GroupTagModel,
        join_on=GroupTagModel.tag_id == TagModel.id,
        schema_to_select=BaseModel,
        filters={"group_id": group.id},
    )
    tag_dict: dict[str, Any] | None = await crud_tags.get_joined(
        db=db,
        tag_name=tag_name.strip(),
        is_deleted=False,
        joins_config=[group_tag_join_config],
        schema_to_select=TagSchema,
    )
    return tag_dict


async def get_or_create_user_tags(
    *,
    tag_names: list[str] = Query(
        examples=[
            ["Essentials", "Fast food"],
            ["Non-essentials", "Car related"],
        ],
        description="List of tag names to filter transactions by",
        default_factory=lambda: [],
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TagModel | TagSchema]:
    tags: list[TagSchema | TagModel] = []
    for tag_name in tag_names:
        tag_dict: dict[str, Any] | None = await _get_user_tag_dict(
            tag_name=tag_name, current_user=current_user, db=db
        )
        if tag_dict is None:
            tag_create_internal = TagCreateInternal(tag_name=tag_name.strip())
            tag_model: TagModel = await crud_tags.create(
                db=db, object=tag_create_internal
            )
            user_tag_create_internal = UserTagCreateInternal(
                user_id=current_user.id,
                user_uuid=current_user.uuid,
                tag_id=tag_model.id,
                tag_uuid=tag_model.uuid,
            )
            await crud_user_tag.create(db=db, object=user_tag_create_internal)
            tags.append(tag_model)
        else:
            tags.append(TagSchema(**tag_dict))

    return tags


async def get_or_create_group_tags(
    *,
    tag_names: list[str] = Query(
        examples=[
            ["Essentials", "Fast food"],
            ["Non-essentials", "Car related"],
        ],
        description="List of tag names to filter transactions by",
        default_factory=lambda: [],
    ),
    group: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TagModel | TagSchema]:
    tags: list[TagSchema | TagModel] = []
    for tag_name in tag_names:
        tag_dict: dict[str, Any] | None = await _get_group_tag_dict(
            tag_name=tag_name, group=group, db=db
        )
        if tag_dict is None:
            tag_create_internal = TagCreateInternal(tag_name=tag_name.strip())
            tag_model: TagModel = await crud_tags.create(
                db=db, object=tag_create_internal
            )
            group_tag_create_internal = GroupTagCreateInternal(
                group_id=group.id,
                group_uuid=group.uuid,
                tag_id=tag_model.id,
                tag_uuid=tag_model.uuid,
            )
            await crud_group_tag.create(db=db, object=group_tag_create_internal)
            tags.append(tag_model)
        else:
            tags.append(TagSchema(**tag_dict))

    return tags


async def get_non_deleted_user_tags(
    *,
    tag_names: list[str] = Query(
        examples=[
            ["Essentials", "Fast food"],
            ["Non-essentials", "Car related"],
        ],
        description="List of tag names to filter transactions by",
        default_factory=lambda: [],
    ),
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TagSchema]:
    tags: list[TagSchema] = []
    for tag_name in tag_names:
        tag_dict: dict[str, Any] | None = await _get_user_tag_dict(
            tag_name=tag_name, current_user=current_user, db=db
        )
        if tag_dict is None:
            raise NotFoundException(f"Tag {tag_name} not found.")
        tags.append(TagSchema(**tag_dict))

    return tags


async def get_non_deleted_group_tags(
    *,
    tag_names: list[str] = Query(
        examples=[
            ["Essentials", "Fast food"],
            ["Non-essentials", "Car related"],
        ],
        description="List of tag names to filter transactions by",
        default_factory=lambda: [],
    ),
    group: Annotated[GroupSchema, Depends(get_non_deleted_user_group)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[TagSchema]:
    tags: list[TagSchema] = []
    for tag_name in tag_names:
        tag_dict: dict[str, Any] | None = await _get_group_tag_dict(
            tag_name=tag_name, group=group, db=db
        )
        if tag_dict is None:
            raise NotFoundException(f"Tag {tag_name} not found.")
        tags.append(TagSchema(**tag_dict))

    return tags
