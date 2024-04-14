from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, Field


class TimeSchema(BaseModel):
    timestamp: Annotated[
        datetime,
        Field(
            examples=[datetime.now(UTC)],
            description="Timestamp must be a valid datetime.",
        ),
    ]


class OptionalTimeSchema(BaseModel):
    timestamp: Annotated[
        datetime | None,
        Field(
            default=None,
            examples=[datetime.now(UTC)],
            description="Timestamp must be a valid datetime.",
        ),
    ]


class CurrentTimeSchema(BaseModel):
    timestamp: Annotated[
        datetime,
        Field(
            default_factory=lambda: datetime.now(UTC),
            examples=[datetime.now(UTC)],
            description="Timestamp must be a valid datetime.",
        ),
    ]


class DismissedSchema(BaseModel):
    dismissed: Annotated[
        bool,
        Field(
            examples=[True, False],
            description="Dismissed must be a boolean.",
        ),
    ]


class OptionalDismissedSchema(BaseModel):
    dismissed: Annotated[
        bool | None,
        Field(
            default=None,
            examples=[True, False],
            description="Dismissed must be a boolean.",
        ),
    ]
