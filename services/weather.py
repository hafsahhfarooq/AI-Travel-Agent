import aiohttp
from fastapi import APIRouter, Query
from config import weather_api_key

weather_router = APIRouter()

@weather_router.get("/")
async def get_weather(city: str = Query(..., description="City name")):
    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&aqi=no"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return {
                "location": data["location"]["name"],
                "country": data["location"]["country"],
                "temperature": data["current"]["temp_c"],
                "condition": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"]
            }
