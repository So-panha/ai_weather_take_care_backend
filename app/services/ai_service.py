import google.genai as genai
from app.core.config import settings
from app.core.exceptions import AppException
import asyncio
import json

SYSTEM_PROMPT = """You are WeatherAI, a friendly and knowledgeable assistant built into a weather care application.

Your expertise covers ONLY these topics:
- Current and forecasted weather conditions
- Weather safety tips (storms, extreme heat, cold, floods, lightning, UV, etc.)
- What to wear or bring based on the weather
- How weather affects health (asthma, allergies, pollen, humidity, seasonal illness)
- Travel tips based on weather conditions
- Outdoor activity planning (hiking, sports, events) based on weather
- Air quality and UV index
- Reading and understanding weather data, forecasts, and maps

Rules:
1. Only answer questions related to the topics above.
2. If the user asks something completely unrelated to weather or the app context, politely say: "I'm your weather assistant — I can only help with weather-related questions! Try asking me about today's forecast, UV levels, or what to wear."
3. Be friendly, concise, and actionable. Use emojis where appropriate.
4. CRITICAL: NEVER ask the user for their location, city, or current weather conditions. The app automatically provides live weather data as context. Use it directly in your answer.
5. If weather data is provided in the context, treat it as the user's actual current weather and reference it naturally (e.g., "Since it's currently 32°C and partly cloudy in Phnom Penh...").
6. If NO weather data is provided, give a general helpful answer based on common weather knowledge. Still do NOT ask the user for weather info.
7. Keep responses short and conversational (3-5 sentences max unless more detail is needed).
"""

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    def _get_client(self):
        if not self.api_key:
            raise AppException(status_code=500, detail="Gemini API key not configured")
        return genai.Client(api_key=self.api_key)

    async def chat(self, user_message: str, weather_data: dict = None) -> str:
        """
        General weather-related chat. Accepts any user message and optional
        live weather data for context.
        """
        client = self._get_client()
        
        # Build contextual prompt
        context_parts = [SYSTEM_PROMPT]
        
        if weather_data:
            try:
                temp = round(weather_data.get("main", {}).get("temp", 0))
                feels_like = round(weather_data.get("main", {}).get("feels_like", 0))
                humidity = weather_data.get("main", {}).get("humidity", 0)
                condition = weather_data.get("weather", [{}])[0].get("description", "")
                city = weather_data.get("name", "your location")
                wind = weather_data.get("wind", {}).get("speed", 0)
                
                context_parts.append(
                    f"\n\nCurrent weather context (use this for personalized answers):\n"
                    f"- Location: {city}\n"
                    f"- Temperature: {temp}°C (feels like {feels_like}°C)\n"
                    f"- Condition: {condition}\n"
                    f"- Humidity: {humidity}%\n"
                    f"- Wind speed: {wind} m/s"
                )
            except Exception:
                pass  # weather_data was malformed, skip context
        
        context_parts.append(f"\n\nUser: {user_message}\nWeatherAI:")
        full_prompt = "".join(context_parts)
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt
                )
            )
            return response.text.strip()
        except Exception as e:
            raise AppException(status_code=500, detail=f"AI request failed: {str(e)}")

    async def analyze_weather(self, weather_data: dict) -> str:
        """Legacy: analyze weather data and give a summary recommendation."""
        return await self.chat(
            "Analyze the current weather and give me a friendly summary with preparation tips.",
            weather_data
        )

ai_service = AIService()
