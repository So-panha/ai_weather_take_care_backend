from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.deps import get_db, CurrentUser
from app.models.user import User
from app.models.consultation_history import ConsultationHistory
from app.schemas.history import ConsultationHistoryResponse, ConsultationHistoryCreate

router = APIRouter()

@router.get("/", response_model=List[ConsultationHistoryResponse])
async def get_history(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ConsultationHistory)
        .where(ConsultationHistory.user_id == current_user.id)
        .order_by(ConsultationHistory.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=ConsultationHistoryResponse)
async def create_history_entry(
    history_in: ConsultationHistoryCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    entry = ConsultationHistory(**history_in.model_dump(), user_id=current_user.id)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
