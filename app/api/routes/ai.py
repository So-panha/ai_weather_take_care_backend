from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.api.deps import CurrentUser
from app.services.ai_service import ai_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's question or message")
    weather_data: Optional[dict] = Field(None, description="Current weather data for context (optional)")

class ChatResponse(BaseModel):
    reply: str

# Keep legacy endpoint for backward compatibility
class WeatherAnalysisRequest(BaseModel):
    weather_data: dict = Field(..., description="JSON representation of OpenWeatherMap response data")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: CurrentUser):
    """
    Send any weather-related message and get a dynamic AI response.
    Optionally pass current weather_data for personalized, context-aware answers.
    """
    reply = await ai_service.chat(request.message, request.weather_data)
    return ChatResponse(reply=reply)

@router.post("/analyze")
async def analyze_weather(request: WeatherAnalysisRequest, current_user: CurrentUser):
    """
    Legacy: Analyze weather data and get AI recommendations.
    """
    analysis = await ai_service.analyze_weather(request.weather_data)
    return {"analysis": analysis}
