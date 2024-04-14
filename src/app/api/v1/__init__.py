from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(users_router)
router.include_router(login_router)
router.include_router(logout_router)
