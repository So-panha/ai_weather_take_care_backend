from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from slowapi import _rate_limit_exceeded_handler
# from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.routes import api_router
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import setup_logging

setup_logging()

# Create FastAPI app instances
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)   

# Apply Rate Limiter
if settings.RATE_LIMITING_ENABLED:
    from app.core.rate_limit import limiter
    app.state.limiter = limiter
    # app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_exception_handler(AppException, app_exception_handler)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include core API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve uploaded files (avatars, etc.)
uploads_dir = Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

@app.get("/")
def root():
    return {"message": "Welcome to AI Weather Care API"}
