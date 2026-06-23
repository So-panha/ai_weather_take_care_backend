import httpx
from datetime import datetime
from app.core.config import settings
from app.core.exceptions import AppException

CONDITION_ICONS = {
    "Clear": "☀️",
    "Clouds": "⛅",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}

def _icon(main: str) -> str:
    return CONDITION_ICONS.get(main, "🌡️")

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = settings.OPENWEATHERMAP_API_KEY

    def _check_key(self):
        if not self.api_key:
            raise AppException(status_code=500, detail="Weather API key not configured")

    async def get_weather_by_city(self, city: str):
        self._check_key()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/weather",
                params={"q": city, "appid": self.api_key, "units": "metric"}
            )
            if response.status_code == 404:
                raise AppException(status_code=404, detail="City not found")
            elif response.status_code != 200:
                raise AppException(status_code=response.status_code, detail="Failed to fetch weather data")
            return response.json()

    async def get_forecast_by_city(self, city: str) -> dict:
        """
        Fetches the OpenWeatherMap 5-day / 3-hour forecast and returns
        structured hourly (next 8 slots = 24h) and daily (7 days) lists.
        """
        self._check_key()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast",
                params={"q": city, "appid": self.api_key, "units": "metric", "cnt": 56}
            )
            if response.status_code == 404:
                raise AppException(status_code=404, detail="City not found")
            elif response.status_code != 200:
                raise AppException(status_code=response.status_code, detail="Failed to fetch forecast data")

        data = response.json()
        items = data.get("list", [])

        # --- Hourly: next 8 slots (= 24 hours, every 3h) ---
        hourly = []
        for item in items[:8]:
            dt = datetime.fromtimestamp(item["dt"])
            main = item["weather"][0]["main"]
            hourly.append({
                "time": dt.strftime("%I%p").lstrip("0"),  # e.g. "3PM"
                "icon": _icon(main),
                "temp": round(item["main"]["temp"]),
                "rainChance": round(item.get("pop", 0) * 100),  # prob of precipitation %
                "condition": item["weather"][0]["description"]
            })

        # --- Daily: group by day, take min/max temp and most common condition ---
        day_buckets: dict[str, dict] = {}
        for item in items:
            day_key = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if day_key not in day_buckets:
                day_buckets[day_key] = {
                    "temps": [],
                    "pops": [],
                    "mains": []
                }
            day_buckets[day_key]["temps"].append(item["main"]["temp"])
            day_buckets[day_key]["pops"].append(item.get("pop", 0))
            day_buckets[day_key]["mains"].append(item["weather"][0]["main"])

        weekly = []
        for day_str, bucket in list(day_buckets.items())[:7]:
            dt = datetime.strptime(day_str, "%Y-%m-%d")
            dominant = max(set(bucket["mains"]), key=bucket["mains"].count)
            weekly.append({
                "day": dt.strftime("%a"),  # e.g. "Mon"
                "icon": _icon(dominant),
                "high": round(max(bucket["temps"])),
                "low": round(min(bucket["temps"])),
                "rainChance": round(max(bucket["pops"]) * 100),
                "condition": dominant
            })

        return {"hourly": hourly, "weekly": weekly}

weather_service = WeatherService()
