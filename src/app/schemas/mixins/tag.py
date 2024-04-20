import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, Field


class TagIDSchema(BaseModel):
    tag_id: Annotated[
        int,
        Field(
            title="Tag ID",
            description="Tag ID is a unique identifier for the tag.",
        ),
    ]


class TagUUIDSchema(BaseModel):
    tag_uuid: Annotated[
        uuid_pkg.UUID,
        Field(
            title="Tag UUID",
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tag UUID must be a valid UUIDv4.",
        ),
    ]


class TagOptionalUUIDSchema(BaseModel):
    tag_uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            default=None,
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="Tag UUID must be a valid UUIDv4.",
        ),
    ]


class TagOptionalIDSchema(BaseModel):
    tag_id: Annotated[
        int | None,
        Field(
            default=None,
            title="Tag ID",
            description="Tag ID is a unique identifier for the tag.",
        ),
    ]
