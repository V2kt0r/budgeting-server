from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)
from ..schemas.purchase_category import PurchaseCategoryBase
from .mixins.purchase_category import (
    PurchaseCategoryIDSchema,
    PurchaseCategoryOptionalIDSchema,
    PurchaseCategoryOptionalUUIDSchema,
    PurchaseCategoryUUIDSchema,
)


class TransactionItemBase(BaseModel):
    amount: Annotated[
        float,
        Field(
            ge=0,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ]
    name: Annotated[
        str | None,
        Field(
            max_length=100,
            examples=["Chips", "Soda", "Milk", "Bread"],
            description="Name of the item.",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            max_length=500,
            examples=[
                "Lays chips",
                "Coca Cola",
                "Milk from Lidl",
                "Bread from Tesco",
            ],
            description="Description or details of the item.",
        ),
    ]


class TransactionItemBaseExternal(
    PurchaseCategoryUUIDSchema, TransactionItemBase
):
    pass


class TransactionItemBaseInternal(
    PurchaseCategoryIDSchema, TransactionItemBaseExternal
):
    pass


class TransactionItem(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    TransactionItemBaseInternal,
):
    pass


class TransactionItemRead(
    PurchaseCategoryBase, UUIDSchema, TransactionItemBaseExternal
):
    tag_names: Annotated[
        list[str],
        Field(
            default=None,
            description="List of tags associated with the item.",
        ),
    ]


class TransactionItemCreate(TransactionItemBaseExternal):
    tag_names: Annotated[
        list[str],
        Field(
            default=None,
            description="List of tags associated with the item.",
            exclude=True,
        ),
    ]


class TransactionItemCreateInternal(TransactionItemBaseInternal):
    pass


class TransactionItemUpdate(PurchaseCategoryOptionalUUIDSchema, BaseModel):
    amount: Annotated[
        float,
        Field(
            ge=0,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ]
    name: Annotated[
        str | None,
        Field(
            max_length=100,
            examples=["Chips", "Soda", "Milk", "Bread"],
            description="Name of the item.",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            max_length=500,
            examples=[
                "Lays chips",
                "Coca Cola",
                "Milk from Lidl",
                "Bread from Tesco",
            ],
            description="Description or details of the item.",
        ),
    ]
    tag_names: Annotated[
        list[str],
        Field(
            default=None,
            description="List of tags associated with the item.",
            exclude=True,
        ),
    ]


class TransactionItemUpdateInternal(
    PurchaseCategoryOptionalIDSchema,
    PurchaseCategoryOptionalUUIDSchema,
    BaseModel,
):
    amount: Annotated[
        float,
        Field(
            ge=0,
            examples=[100.0, 200.0, 300.0],
            description="Value of the transaction.",
        ),
    ]
    name: Annotated[
        str | None,
        Field(
            max_length=100,
            examples=["Chips", "Soda", "Milk", "Bread"],
            description="Name of the item.",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            max_length=500,
            examples=[
                "Lays chips",
                "Coca Cola",
                "Milk from Lidl",
                "Bread from Tesco",
            ],
            description="Description or details of the item.",
        ),
    ]


class TransactionItemDelete(BaseModel):
    pass
