from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastcrud.paginated import (
    PaginatedListResponse,
    compute_offset,
    paginated_response,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from ...core.schemas.utils import Message
from ...core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...crud.crud_users import crud_users
from ...models.tier import Tier
from ...models.user import User as UserModel
from ...schemas.tier import TierRead
from ...schemas.user import User as UserSchema
from ...schemas.user import (
    UserCreate,
    UserCreateInternal,
    UserRead,
    UserTierUpdate,
    UserUpdate,
)

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserRead, status_code=201)
async def write_user(
    request: Request,
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    email_exists: bool = await crud_users.exists(db=db, email=user_create.email)
    if email_exists:
        raise DuplicateValueException("Email is already registered")

    username_exists: bool = await crud_users.exists(
        db=db, username=user_create.username
    )
    if username_exists:
        raise DuplicateValueException("Username not available")

    if user_create.tier_uuid is not None:
        tier_exists: bool = await crud_tiers.exists(
            db=db, uuid=user_create.tier_uuid
        )
        if not tier_exists:
            raise NotFoundException("Tier not found")

    user_internal_dict: dict = user_create.model_dump()
    user_internal_dict["hashed_password"] = get_password_hash(
        password=user_internal_dict["password"]
    )
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    user_model: UserModel = await crud_users.create(
        db=db,
        object=user_internal,
    )
    return user_model


@router.get("/users", response_model=PaginatedListResponse[UserRead])
async def read_users(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Any:
    users_data: dict[str, Any] = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=UserRead,
        is_deleted=False,
    )

    return paginated_response(
        crud_data=users_data, page=page, items_per_page=items_per_page
    )


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
) -> Any:
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    user_read: UserRead | None = await crud_users.get(
        db=db,
        return_as_model=True,
        schema_to_select=UserRead,
        username=username,
        is_deleted=False,
    )
    if user_read is None:
        raise NotFoundException("User not found")

    return user_read


@router.patch("/user/{username}", response_model=Message)
async def patch_user(
    request: Request,
    user_update: UserUpdate,
    username: str,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    user_read: UserRead | None = await crud_users.get(
        db=db,
        return_as_model=True,
        schema_to_select=UserRead,
        username=username,
        is_deleted=False,
    )
    if user_read is None:
        raise NotFoundException("User not found")

    if user_read.username != current_user.username:
        raise ForbiddenException()

    if user_update.username != user_read.username:
        username_exists: bool = await crud_users.exists(
            db=db, username=user_update.username
        )
        if username_exists:
            raise DuplicateValueException("Username not available")

    if user_update.email != user_read.email:
        email_exists: bool = await crud_users.exists(
            db=db, email=user_update.email
        )
        if email_exists:
            raise DuplicateValueException("Email is already registered")

    await crud_users.update(db=db, object=user_update, username=username)
    return Message(message="User updated")


@router.delete("/user/{username}", response_model=Message)
async def erase_user(
    request: Request,
    username: str,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Message:
    user_read: UserRead | None = await crud_users.get(
        db=db,
        return_as_model=True,
        schema_to_select=UserRead,
        username=username,
    )
    if not user_read:
        raise NotFoundException("User not found")

    if username != current_user.username:
        raise ForbiddenException()

    await crud_users.delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return Message(message="User deleted")


@router.delete(
    "/db_user/{username}",
    dependencies=[Depends(get_current_superuser)],
    response_model=Message,
)
async def erase_db_user(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Message:
    user_exists: bool = await crud_users.exists(db=db, username=username)
    if not user_exists:
        raise NotFoundException("User not found")

    await crud_users.db_delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return Message(message="User deleted from the database")


@router.get(
    "/user/{username}/rate_limits",
    dependencies=[Depends(get_current_superuser)],
    # TODO: Add pagination
    # TODO: Add response model
)
async def read_user_rate_limits(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    user_read: dict | None = await crud_users.get(
        db=db, username=username, schema_to_select=UserRead
    )
    if user_read is None:
        raise NotFoundException("User not found")

    if user_read["tier_uuid"] is None:
        user_read["tier_rate_limits"] = []
        return user_read

    db_tier: TierRead | None = await crud_tiers.get(
        db=db,
        uuid=user_read["tier_uuid"],
        return_as_model=True,
        schema_to_select=TierRead,
    )
    if db_tier is None:
        raise NotFoundException("Tier not found")

    db_rate_limits: dict[str, Any] = await crud_rate_limits.get_multi(
        db=db, tier_uuid=db_tier.uuid
    )

    user_read["tier_rate_limits"] = db_rate_limits["data"]

    return user_read


# TODO: Add response model
# TODO: Figure out how to handle the ruff warning on join_model
@router.get("/user/{username}/tier")
async def read_user_tier(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict | None:
    user_read: UserRead = await crud_users.get(
        db=db,
        username=username,
        return_as_model=True,
        schema_to_select=UserRead,
    )
    if user_read is None:
        raise NotFoundException("User not found")

    tier_exists: bool = await crud_tiers.exists(db=db, uuid=user_read.tier_uuid)
    if not tier_exists:
        raise NotFoundException("Tier not found")

    joined: dict = await crud_users.get_joined(
        db=db,
        join_model=Tier,
        join_prefix="tier_",
        schema_to_select=UserRead,
        join_schema_to_select=TierRead,
        username=username,
    )

    return joined


@router.patch(
    "/user/{username}/tier",
    dependencies=[Depends(get_current_superuser)],
    response_model=Message,
)
async def patch_user_tier(
    request: Request,
    username: str,
    user_tier_update: UserTierUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    user_read: UserRead | None = await crud_users.get(
        db=db,
        username=username,
        return_as_model=True,
        schema_to_select=UserRead,
    )
    if user_read is None:
        raise NotFoundException("User not found")

    if user_tier_update.tier_uuid is not None:
        tier_exists: bool = await crud_tiers.exists(
            db=db, uuid=user_tier_update.tier_uuid
        )
        if not tier_exists:
            raise NotFoundException("Tier not found")

    await crud_users.update(db=db, object=user_tier_update, username=username)
    return Message(message=f"User {user_read.username} Tier updated")
