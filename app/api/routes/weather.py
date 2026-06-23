from fastapi import APIRouter
from app.api.deps import CurrentUser
from app.services.weather_service import weather_service

router = APIRouter()

@router.get("/")
async def get_weather(city: str, current_user: CurrentUser):
    """Get current weather for a specific city. Requires authentication."""
    return await weather_service.get_weather_by_city(city)

@router.get("/forecast")
async def get_forecast(city: str, current_user: CurrentUser):
    """
    Get 5-day forecast for a city, returning structured hourly (24h) and
    daily (7-day) data with temperature, rain chance and weather icons.
    """
    return await weather_service.get_forecast_by_city(city)
