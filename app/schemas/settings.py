from pydantic import BaseModel, Field
from typing import Optional

class UserPreferencesBase(BaseModel):
    dark_mode: bool = True
    compact_view: bool = False
    reduce_animations: bool = False
    push_alerts: bool = True
    storm_warning: bool = True
    location_services: bool = True

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferencesResponse(UserPreferencesBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class PaymentMethodBase(BaseModel):
    card_type: str
    last4: str
    expiry: str
    is_default: bool = False
    bg_gradient: Optional[str] = None

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodResponse(PaymentMethodBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
