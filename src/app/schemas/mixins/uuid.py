import uuid as uuid_pkg
from typing import Annotated

from pydantic import BaseModel, Field


class OptionalUUIDSchema(BaseModel):
    uuid: Annotated[
        uuid_pkg.UUID | None,
        Field(
            default=None,
            examples=[uuid_pkg.uuid4(), uuid_pkg.uuid4(), uuid_pkg.uuid4()],
            description="UUID must be a valid UUIDv4.",
        ),
    ]
