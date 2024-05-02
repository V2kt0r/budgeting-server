from fastapi import APIRouter

from .group import router as group_router
from .group_transactions import router as group_transactions_router
from .login import router as login_router
from .logout import router as logout_router
from .user_transactions import router as user_transactions_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(user_transactions_router)
router.include_router(group_router)
router.include_router(group_transactions_router)
