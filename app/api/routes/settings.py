from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from app.api.deps import get_db, CurrentUser
from app.models.user import User
from app.models.payment_method import PaymentMethod
from app.models.user_preferences import UserPreference
from app.schemas.settings import (
    UserPreferencesResponse, UserPreferencesUpdate, 
    PaymentMethodResponse, PaymentMethodCreate
)

router = APIRouter()

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    result = await db.execute(stmt)
    prefs = result.scalars().first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)
    return prefs

@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_in: UserPreferencesUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    result = await db.execute(stmt)
    prefs = result.scalars().first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
        
    for field, value in preferences_in.model_dump().items():
        setattr(prefs, field, value)
        
    await db.commit()
    await db.refresh(prefs)
    return prefs

@router.get("/payments", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PaymentMethod).where(PaymentMethod.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/payments", response_model=PaymentMethodResponse)
async def add_payment_method(
    payment_in: PaymentMethodCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    payment = PaymentMethod(**payment_in.model_dump(), user_id=current_user.id)
    if payment.is_default:
        # Reset others
        stmt = (
            update(PaymentMethod)
            .where(PaymentMethod.user_id == current_user.id)
            .values(is_default=False)
        )
        await db.execute(stmt)
        
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment
