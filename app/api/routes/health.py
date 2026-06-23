from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.deps import get_db

router = APIRouter()

@router.get("/health")
def health_check():
    """ Basic health check endpoint. """
    return {"status": "ok"}

@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """ Check if Database responds properly. """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "up"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

@router.get("/liveness")
def liveness_check():
    """ Component checks (e.g., container running). """
    return {"status": "alive"}
