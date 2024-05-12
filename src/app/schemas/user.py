import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)
from .links.group_user import GroupUserBase
from .mixins.uuid import OptionalUUIDSchema


class UserBase(BaseModel):
    username: Annotated[
        str,
        Field(
            min_length=2,
            max_length=30,
            examples=["JohnDoe"],
            description="Username must be unique and between 2 and 30 characters long.",
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            max_length=50,
            examples=["john.doe@example.com"],
            description="Email must be unique and less than 50 characters long.",
        ),
    ]


class UserBaseExternal(UserBase):
    tier_uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            default=None,
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tier UUID must be a valid UUIDv4.",
        ),
    ]


class UserBaseInternal(UserBaseExternal):
    tier_id: int | None = None


class User(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    UserBaseInternal,
):
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            default=None,
            examples=["https://www.profileimageurl.com"],
            description="Profile image URL must be a valid URL.",
        ),
    ]
    hashed_password: str
    is_superuser: bool = False


class UserRead(UUIDSchema, UserBaseExternal):
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            default=None,
            examples=["https://www.profileimageurl.com"],
            description="Profile image URL must be a valid URL.",
        ),
    ]


class UserReadWithUserRole(GroupUserBase, UserRead):
    pass


class UserCreate(UserBaseExternal):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[
        str,
        Field(
            min_length=8,
            examples=["Password123!"],
            description="Password must be at least 8 characters long.",
        ),
    ]


class UserCreateInternal(UserBaseInternal):
    hashed_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Annotated[
        str | None,
        Field(
            min_length=2,
            max_length=30,
            default=None,
            examples=["JohnDoe"],
            description="Username must be unique and between 2 and 30 characters long.",
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            max_length=50,
            examples=["john.doe@example.com"],
            description="Email must be unique and less than 50 characters long.",
        ),
    ]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            default=None,
            examples=["https://www.profileimageurl.com"],
            description="Profile image URL must be a valid URL.",
        ),
    ]


class UserUpdateInternal(OptionalUUIDSchema, UserUpdate):
    pass


class UserTierUpdate(BaseModel):
    tier_uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tier UUID must be a valid UUIDv4.",
        ),
    ]


class UserTierUpdateInternal(BaseModel):
    tier_id: int


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserRestoreDeleted(BaseModel):
    is_deleted: bool = False
