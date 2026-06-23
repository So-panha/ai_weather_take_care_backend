from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConsultationHistoryBase(BaseModel):
    title: str
    text: str
    tags: List[str]
    icon: str

class ConsultationHistoryCreate(ConsultationHistoryBase):
    pass

class ConsultationHistoryResponse(ConsultationHistoryBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
