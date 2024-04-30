from fastcrud import FastCRUD

from ...models.links.group_purchase_category import GroupPurchaseCategory
from ...schemas.links.group_purchase_category import (
    GroupPurchaseCategoryCreateInternal,
    GroupPurchaseCategoryDelete,
    GroupPurchaseCategoryUpdate,
    GroupPurchaseCategoryUpdateInternal,
)

CRUDGroupPurchaseCategory = FastCRUD[
    GroupPurchaseCategory,
    GroupPurchaseCategoryCreateInternal,
    GroupPurchaseCategoryUpdate,
    GroupPurchaseCategoryUpdateInternal,
    GroupPurchaseCategoryDelete,
]
crud_group_purchase_category = CRUDGroupPurchaseCategory(GroupPurchaseCategory)
