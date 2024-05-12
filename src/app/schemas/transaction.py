from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)
from ..models.transaction import Currency
from .mixins.misc import CurrentTimeSchema
from .mixins.purchase_category import PurchaseCategoryOptionalUUIDSchema
from .transaction_item import TransactionItemCreate, TransactionItemRead


class TransactionBase(CurrentTimeSchema, BaseModel):
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


class TransactionBaseExternal(TransactionBase):
    pass


class TransactionBaseInternal(TransactionBaseExternal):
    pass


class Transaction(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    TransactionBaseInternal,
):
    pass


class TransactionRead(UUIDSchema, TransactionBaseExternal):
    transaction_items: Annotated[
        list[TransactionItemRead],
        Field(
            default_factory=lambda: [],
            description="List of items associated with the transaction.",
        ),
    ]


class TransactionCreate(
    PurchaseCategoryOptionalUUIDSchema, TransactionBaseExternal
):
    tag_names: Annotated[
        list[str],
        Field(
            default_factory=lambda: [],
            description="List of tags associated with the transaction.",
            exclude=True,
        ),
    ]
    transaction_items: Annotated[
        list[TransactionItemCreate],
        Field(
            default_factory=lambda: [],
            description="List of items associated with the transaction.",
        ),
    ]


class TransactionCreateInternal(TransactionBaseInternal):
    pass


class TransactionUpdate(PurchaseCategoryOptionalUUIDSchema, BaseModel):
    amount: Annotated[
        float,
        Field(
            ge=0,
            default=None,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ]
    currency: Annotated[
        Currency,
        Field(
            default=None,
            examples=[currency for currency in Currency],
            description="Currency of the transaction.",
        ),
    ]
    name: Annotated[
        str,
        Field(
            max_length=100,
            default=None,
            examples=["LIDL purchase", "Rent payment", "Netflix subscription"],
            description="Name or title of the transaction.",
        ),
    ]
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
    tag_names: Annotated[
        list[str],
        Field(
            default_factory=lambda: [],
            description="List of tags associated with the transaction.",
            exclude=True,
        ),
    ]
    transaction_items: Annotated[
        list[TransactionItemCreate],
        Field(
            default_factory=lambda: [],
            description="List of items associated with the transaction.",
        ),
    ]


class TransactionUpdateInternal(BaseModel):
    amount: Annotated[
        float,
        Field(
            ge=0,
            default=None,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ]
    currency: Annotated[
        Currency,
        Field(
            default=None,
            examples=[currency for currency in Currency],
            description="Currency of the transaction.",
        ),
    ]
    name: Annotated[
        str,
        Field(
            max_length=100,
            default=None,
            examples=["LIDL purchase", "Rent payment", "Netflix subscription"],
            description="Name or title of the transaction.",
        ),
    ]
    description: Annotated[
        str,
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
    ]


class TransactionDelete(BaseModel):
    pass
