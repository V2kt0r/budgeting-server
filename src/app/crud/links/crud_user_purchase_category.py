from fastcrud import FastCRUD

from ...models.links.user_purchase_category import UserPurchaseCategory
from ...schemas.links.user_purchase_category import (
    UserPurchaseCategoryCreateInternal,
    UserPurchaseCategoryDelete,
    UserPurchaseCategoryUpdate,
    UserPurchaseCategoryUpdateInternal,
)

CRUDUserPurchaseCategory = FastCRUD[
    UserPurchaseCategory,
    UserPurchaseCategoryCreateInternal,
    UserPurchaseCategoryUpdate,
    UserPurchaseCategoryUpdateInternal,
    UserPurchaseCategoryDelete,
]
crud_user_purchase_category = CRUDUserPurchaseCategory(UserPurchaseCategory)
