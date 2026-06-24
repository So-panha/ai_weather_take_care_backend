from fastapi.responses import JSONResponse
from fastapi import Request
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
from contextlib import asynccontextmanager 
from app.database import engine, Base 
import app.models  # Ensure all models are imported for Base.metadata


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    logging.info("Checking database tables...")
    try:
        # This securely connects to Render PostgreSQL and creates tables if missing
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database tables initialized successfully!")
    except Exception as e:
        logging.error(f"Failed to auto-initialize database tables: {e}")
    
    yield  # The app runs while execution is paused here

# Create FastAPI app instances with lifespan attached
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan  # <-- ATTACHED LIFESPAN HERE
)

# Apply Rate Limiter
if settings.RATE_LIMITING_ENABLED:
    from app.core.rate_limit import limiter
    app.state.limiter = limiter
    # app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_exception_handler(AppException, app_exception_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    import logging
    logging.error(f"Unhandled exception: {exc}")
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please check backend logs."},
    )

# Set all CORS enabled origins
origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

# Add Vercel and local origins for convenience if "*" or generic list
if "*" in origins or len(origins) <= 1:
    origins.extend([
        "https://ai-weather-take-care-frontend.vercel.app",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
    ])

# Remove duplicates
origins = list(set(origins))
if "*" in origins and len(origins) > 1:
    origins.remove("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
