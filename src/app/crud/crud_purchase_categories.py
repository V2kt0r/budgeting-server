from fastcrud import FastCRUD

from ..models.purchase_category import PurchaseCategory
from ..schemas.purchase_category import (
    PurchaseCategoryCreateInternal,
    PurchaseCategoryDelete,
    PurchaseCategoryUpdateInternal,
    PurchaseCategoryUpdate,
)

CRUDPurchaseCategory = FastCRUD[
    PurchaseCategory,
    PurchaseCategoryCreateInternal,
    PurchaseCategoryUpdate,
    PurchaseCategoryUpdateInternal,
    PurchaseCategoryDelete,
]
crud_purchase_categories = CRUDPurchaseCategory(PurchaseCategory)
