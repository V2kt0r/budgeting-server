import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)


def sanitize_path(path: str) -> str:
    return path.strip("/").replace("/", "_")


class RateLimitBase(BaseModel):
    path: Annotated[
        str,
        Field(
            max_length=100,
            examples=["users"],
            description="Path is the URL path to be rate limited.",
        ),
    ]
    limit: Annotated[
        int,
        Field(
            ge=1,
            examples=[5],
            description="Limit is the number of requests allowed within the period.",
        ),
    ]
    period: Annotated[
        int,
        Field(
            ge=1,
            examples=[60],
            description="Period is the time in seconds that the limit is enforced.",
        ),
    ]

    @field_validator("path")
    def validate_and_sanitize_path(cls, v: str) -> str:
        return sanitize_path(v)


class RateLimitBaseExternal(UUIDSchema, RateLimitBase):
    tier_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            min_length=36,
            max_length=36,
            pattern="^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tier UUID must be a valid UUIDv4.",
        ),
    ]


class RateLimitBaseInternal(IDSchema, RateLimitBase):
    tier_id: int


class RateLimit(
    TimestampSchema,
    PersistentDeletionSchema,
    RateLimitBaseExternal,
    RateLimitBaseInternal,
):
    name: Annotated[str | None, Field(default=None, examples=["users:5:60"])]


class RateLimitRead(RateLimitBaseExternal):
    name: str = Field(..., examples=["users:5:60"])


class RateLimitCreate(RateLimitBase):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str | None, Field(default=None, examples=["api_v1_users:5:60"])
    ]


class RateLimitCreateInternal(RateLimitCreate):
    tier_id: int


class RateLimitUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str | None = Field(
        default=None,
        max_length=100,
        examples=["users"],
        description="Path is the URL path to be rate limited.",
    )
    limit: int | None = Field(
        ge=1,
        examples=[5],
        description="Limit is the number of requests allowed within the period.",
    )
    period: int | None = Field(
        ge=1,
        examples=[60],
        description="Period is the time in seconds that the limit is enforced.",
    )
    name: str | None = Field(examples=["users:5:60"])

    @field_validator("path")
    def validate_and_sanitize_path(cls, v: str) -> str | None:
        return sanitize_path(v) if v is not None else None


class RateLimitUpdateInternal(RateLimitUpdate):
    uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            min_length=36,
            max_length=36,
            pattern="^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID of the rate limit to update. Must be a valid UUIDv4.",
        ),
    ]


class RateLimitDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RateLimitRestoreDeleted(BaseModel):
    is_deleted: bool = False
