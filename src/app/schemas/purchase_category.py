from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas.mixins import (
    IDSchema,
    PersistentDeletionSchema,
    TimestampSchema,
    UUIDSchema,
)


class PurchaseCategoryBase(BaseModel):
    category_name: Annotated[
        str,
        Field(
            examples=[
                "Groceries",
                "Rent",
                "Utilities",
                "Entertainment",
                "Healthcare",
                "Transportation",
                "Education",
                "Clothing",
                "Electronics",
                "Other",
            ],
            description="Name of the purchase category.",
        ),
    ]
    category_description: Annotated[
        str | None,
        Field(
            max_length=500,
            examples=[
                "Monthly groceries",
                "Apartment rent",
                "Monthly utilities",
                "Monthly entertainment",
                "Healthcare expenses",
                "Transportation expenses",
                "Education expenses",
                "Clothing expenses",
                "Electronics expenses",
                "Other expenses",
            ],
            description="Description or details of the purchase category.",
        ),
    ] = None


class PurchaseCategoryBaseExternal(PurchaseCategoryBase):
    pass


class PurchaseCategoryBaseInternal(PurchaseCategoryBaseExternal):
    pass


class PurchaseCategory(
    IDSchema,
    UUIDSchema,
    TimestampSchema,
    PersistentDeletionSchema,
    PurchaseCategoryBaseInternal,
):
    pass


class PurchaseCategoryRead(PurchaseCategoryBaseExternal):
    pass


class PurchaseCategoryCreate(PurchaseCategoryBaseExternal):
    model_config = ConfigDict(extra="forbid")


class PurchaseCategoryCreateInternal(PurchaseCategoryBaseInternal):
    pass


class PurchaseCategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_name: Annotated[
        str | None,
        Field(
            examples=[
                "Groceries",
                "Rent",
                "Utilities",
                "Entertainment",
                "Healthcare",
                "Transportation",
                "Education",
                "Clothing",
                "Electronics",
                "Other",
            ],
            description="Name of the purchase category.",
        ),
    ] = None
    category_description: Annotated[
        str | None,
        Field(
            max_length=500,
            examples=[
                "Monthly groceries",
                "Apartment rent",
                "Monthly utilities",
                "Monthly entertainment",
                "Healthcare expenses",
                "Transportation expenses",
                "Education expenses",
                "Clothing expenses",
                "Electronics expenses",
                "Other expenses",
            ],
            description="Description or details of the purchase category.",
        ),
    ] = None


class PurchaseCategoryUpdateInternal(PurchaseCategoryUpdate):
    pass


class PurchaseCategoryDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
