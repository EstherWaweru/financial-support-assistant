from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.conversation import router as conversation_router
from app.api.routes.user import router as user_router
from app.api.routes.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(
    conversation_router, prefix="/conversation", tags=["conversation"]
)
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
