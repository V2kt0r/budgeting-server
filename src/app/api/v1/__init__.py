from fastapi import APIRouter

from .group import router as group_router
from .group_purchase_category import router as group_purchase_category_router
from .group_transactions import router as group_transactions_router
from .group_user import router as group_user_router
from .login import router as login_router
from .logout import router as logout_router
from .user_purchase_category import router as user_purchase_category_router
from .user_transaction_items import router as user_transaction_items_router
from .user_transactions import router as user_transactions_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(user_purchase_category_router)
router.include_router(user_transactions_router)
router.include_router(user_transaction_items_router)
router.include_router(group_router)
router.include_router(group_user_router)
router.include_router(group_purchase_category_router)
router.include_router(group_transactions_router)
