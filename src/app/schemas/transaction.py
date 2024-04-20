from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)

from ..models.transaction import Currency
from .mixins.misc import TimeSchema
from .mixins.purchase_category import (
    PurchaseCategoryIDSchema,
    PurchaseCategoryOptionalIDSchema,
    PurchaseCategoryOptionalUUIDSchema,
    PurchaseCategoryUUIDSchema,
)
from .mixins.tag import TagOptionalIDSchema, TagOptionalUUIDSchema


class TransactionBase(TimeSchema, BaseModel):
    amount: Annotated[
        float,
        Field(
            ge=0,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ]
    currency: Annotated[
        Currency,
        Field(
            examples=[currency for currency in Currency],
            description="Currency of the transaction.",
        ),
    ]
    name: Annotated[
        str | None,
        Field(
            max_length=100,
            examples=["LIDL purchase", "Rent payment", "Netflix subscription"],
            description="Name or title of the transaction.",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            max_length=500,
            examples=[
                "Monthly groceries",
                "Apartment rent",
                "Monthly subscription",
            ],
            description="Description or details of the transaction.",
        ),
    ]


class TransactionBaseExternal(
    PurchaseCategoryUUIDSchema, TagOptionalUUIDSchema, TransactionBase
):
    pass


class TransactionBaseInternal(
    PurchaseCategoryIDSchema, TagOptionalIDSchema, TransactionBaseExternal
):
    pass


class Transaction(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    TransactionBaseInternal,
):
    pass


class TransactionRead(TransactionBaseExternal):
    pass


class TransactionCreate(TransactionBaseExternal):
    pass


class TransactionCreateInternal(TransactionBaseInternal):
    pass


class TransactionUpdate(
    PurchaseCategoryOptionalUUIDSchema, TagOptionalUUIDSchema, BaseModel
):
    amount: Annotated[
        float | None,
        Field(
            ge=0,
            default=None,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ] = None
    currency: Annotated[
        Currency | None,
        Field(
            default=None,
            examples=[currency for currency in Currency],
            description="Currency of the transaction.",
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            max_length=100,
            default=None,
            examples=["LIDL purchase", "Rent payment", "Netflix subscription"],
            description="Name or title of the transaction.",
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(
            max_length=500,
            default=None,
            examples=[
                "Monthly groceries",
                "Apartment rent",
                "Monthly subscription",
            ],
            description="Description or details of the transaction.",
        ),
    ] = None


class TransactionUpdateInternal(
    PurchaseCategoryOptionalIDSchema, TagOptionalIDSchema, TransactionUpdate
):
    pass


class TransactionDelete(BaseModel):
    pass
