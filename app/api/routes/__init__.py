from fastapi import APIRouter
from app.api.routes import auth, users, weather, ai, health, settings as settings_route, history

api_router = APIRouter()

api_router.include_router(health.router, tags=["monitoring"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai chatbot"])
api_router.include_router(settings_route.router, prefix="/settings", tags=["settings"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
