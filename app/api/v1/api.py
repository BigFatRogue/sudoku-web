from fastapi import APIRouter

from .routes.router_sudoku import sudoku_router
from .routes.routes_user import users_router
from .routes.router_auth import auth_router
from app.core.enums import TagsEnum


router_api_v1 = APIRouter()
router_api_v1.include_router(sudoku_router)
router_api_v1.include_router(users_router)
router_api_v1.include_router(auth_router)

