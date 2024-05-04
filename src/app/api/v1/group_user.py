import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Request,
    Response,
)
from fastcrud import JoinConfig
from fastcrud.paginated import PaginatedListResponse, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user import User as UserModel

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    ForbiddenException,
    NotFoundException,
)
from ...core.schemas.utils import Message
from ...crud.crud_groups import crud_groups
from ...crud.crud_users import crud_users
from ...crud.links.crud_group_user import crud_group_user
from ...models.links.group_user import UserRole
from ...models.links.group_user import GroupUser as GroupUserModel
from ...schemas.group import Group as GroupSchema
from ...schemas.links.group_user import (
    GroupUserBase,
    GroupUserCreateInternal,
    GroupUserUpdateInternal,
)
from ...schemas.user import User as UserSchema, UserReadWithUserRole
from ..dependencies import get_current_user

router = APIRouter(tags=["Group Members"])


@router.post(
    "/group/{group_uuid}/users/{username}",
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
    username: Annotated[
        str,
        Path(
            min_length=2,
            max_length=30,
            description="The username of the user",
            examples=["JohnDoe", "JaneDoe", "JohnSmith"],
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
    # Check if current user is the same as the user being added
    if current_user.username == username:
        raise ForbiddenException("You cannot add yourself to a group")

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
        username=username,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=UserSchema,
    )
    if user_schema is None:
        raise NotFoundException("The user with this UUID does not exist")

    # Check if user is already in the group
    user_in_group: bool = await crud_group_user.exists(
        db=db, group_uuid=group_uuid, user_uuid=user_schema.uuid
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


@router.get(
    "/group/{group_uuid}/users",
    response_model=PaginatedListResponse[UserReadWithUserRole],
)
async def get_group_users(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the group",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = Query(ge=1, default=1),
    items_per_page: int = Query(ge=1, le=100, default=10),
) -> Any:
    # Check if group exists
    group_exists: bool = await crud_groups.exists(
        db=db, uuid=group_uuid, is_deleted=False
    )
    if not group_exists:
        raise NotFoundException("The group with this UUID does not exist")

    # Check if user is in the group
    user_in_group: bool = await crud_group_user.exists(
        db=db,
        group_uuid=group_uuid,
        user_uuid=current_user.uuid,
    )
    if not user_in_group:
        raise ForbiddenException()

    # Get group users
    group_user_join_config = JoinConfig(
        model=GroupUserModel,
        join_on=GroupUserModel.user_id == UserModel.id,
        schema_to_select=GroupUserBase,
        filters={"group_uuid": group_uuid},
    )
    crud_data: dict[str, Any] = await crud_users.get_multi_joined(
        db=db,
        is_deleted=False,
        joins_config=[group_user_join_config],
        return_as_model=False,
        schema_to_select=UserReadWithUserRole,
    )
    return paginated_response(
        crud_data=crud_data, page=page, items_per_page=items_per_page
    )


@router.put("/group/{group_uuid}/users/{username}", response_model=Message)
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
    username: Annotated[
        str,
        Path(
            min_length=2,
            max_length=30,
            description="The username of the user",
            examples=["JohnDoe", "JaneDoe", "JohnSmith"],
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
    # Check if current user is the same as the user to be updated
    if current_user.username == username:
        raise ForbiddenException("You cannot change your own role")

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
        username=username,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=UserSchema,
    )
    if user_schema is None:
        raise NotFoundException("The user with this UUID does not exist")

    # Check if user is in the group
    user_in_group: bool = await crud_group_user.exists(
        db=db, group_uuid=group_uuid, user_uuid=user_schema.uuid
    )
    if not user_in_group:
        raise NotFoundException("The user is not in the group")

    # Change user role
    await crud_group_user.update(
        db=db,
        group_uuid=group_uuid,
        user_uuid=user_schema.uuid,
        object=GroupUserUpdateInternal(user_role=user_role),
    )
    return Message(message="User role updated")


@router.delete("/group/{group_uuid}/users/{username}", response_model=Message)
async def remove_group_user(
    *,
    request: Request,
    group_uuid: Annotated[
        uuid_pkg.UUID,
        Path(
            description="The UUID of the group",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
        ),
    ],
    username: Annotated[
        str,
        Path(
            min_length=2,
            max_length=30,
            description="The username of the user",
            examples=["JohnDoe", "JaneDoe", "JohnSmith"],
        ),
    ],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    # Check if current user is the same as the user to be removed
    if current_user.username == username:
        raise ForbiddenException("You cannot remove yourself from the group")

    # Check if group exists
    group_exists: bool = await crud_groups.exists(
        db=db, uuid=group_uuid, is_deleted=False
    )
    if not group_exists:
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
        username=username,
        is_deleted=False,
        return_as_model=True,
        schema_to_select=UserSchema,
    )
    if user_schema is None:
        raise NotFoundException("The user with this UUID does not exist")

    # Check if user is in the group
    user_in_group: bool = await crud_group_user.exists(
        db=db, group_uuid=group_uuid, user_uuid=user_schema.uuid
    )
    if not user_in_group:
        raise NotFoundException("The user is not in the group")

    # Remove user from group
    await crud_group_user.delete(
        db=db, group_uuid=group_uuid, user_uuid=user_schema.uuid
    )
    return Message(message="User removed from group")
