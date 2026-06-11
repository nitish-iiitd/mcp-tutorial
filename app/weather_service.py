from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class CityLocation:
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: str


DEFAULT_CITIES: dict[str, CityLocation] = {
    "bengaluru": CityLocation("Bengaluru", "India", 12.9716, 77.5946, "Asia/Kolkata"),
    "delhi": CityLocation("Delhi", "India", 28.6139, 77.2090, "Asia/Kolkata"),
    "mumbai": CityLocation("Mumbai", "India", 19.0760, 72.8777, "Asia/Kolkata"),
    "london": CityLocation("London", "United Kingdom", 51.5072, -0.1276, "Europe/London"),
    "new york": CityLocation("New York", "United States", 40.7128, -74.0060, "America/New_York"),
}

WEATHER_CODE_SUMMARY = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


async def resolve_city(city: str) -> CityLocation:
    city_key = city.strip().lower()
    if city_key in DEFAULT_CITIES:
        return DEFAULT_CITIES[city_key]

    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        response.raise_for_status()
        payload = response.json()

    results = payload.get("results") or []
    if not results:
        raise ValueError(f"Could not find location for city: {city}")

    item = results[0]
    return CityLocation(
        name=item["name"],
        country=item.get("country", "Unknown"),
        latitude=float(item["latitude"]),
        longitude=float(item["longitude"]),
        timezone=item.get("timezone", "auto"),
    )


async def get_current_weather_data(city: str) -> dict[str, Any]:
    location = await resolve_city(city)
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location.latitude,
                "longitude": location.longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": location.timezone,
            },
        )
        response.raise_for_status()
        payload = response.json()

    current = payload["current"]
    code = int(current.get("weather_code", -1))
    return {
        "city": location.name,
        "country": location.country,
        "timezone": payload.get("timezone", location.timezone),
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "condition": WEATHER_CODE_SUMMARY.get(code, f"Weather code {code}"),
        "observed_at": current.get("time"),
        "source": "Open-Meteo public API",
    }


async def get_forecast_data(city: str, days: int = 3) -> dict[str, Any]:
    safe_days = max(1, min(days, 7))
    location = await resolve_city(city)
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location.latitude,
                "longitude": location.longitude,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
                "forecast_days": safe_days,
                "timezone": location.timezone,
            },
        )
        response.raise_for_status()
        payload = response.json()

    daily = payload["daily"]
    items = []
    for index, date in enumerate(daily["time"]):
        code = int(daily["weather_code"][index])
        items.append(
            {
                "date": date,
                "condition": WEATHER_CODE_SUMMARY.get(code, f"Weather code {code}"),
                "max_temp_c": daily["temperature_2m_max"][index],
                "min_temp_c": daily["temperature_2m_min"][index],
                "precipitation_probability_percent": daily["precipitation_probability_max"][index],
                "max_wind_speed_kmh": daily["wind_speed_10m_max"][index],
            }
        )

    return {
        "city": location.name,
        "country": location.country,
        "timezone": payload.get("timezone", location.timezone),
        "days": items,
        "source": "Open-Meteo public API",
    }


async def compare_weather_data(cities: list[str]) -> dict[str, Any]:
    if not cities:
        raise ValueError("At least one city is required")
    limited_cities = cities[:5]
    results = []
    for city in limited_cities:
        results.append(await get_current_weather_data(city))

    coolest = min(results, key=lambda item: item["temperature_c"])
    warmest = max(results, key=lambda item: item["temperature_c"])
    return {
        "compared_cities": results,
        "summary": {
            "warmest": f"{warmest['city']} at {warmest['temperature_c']}°C",
            "coolest": f"{coolest['city']} at {coolest['temperature_c']}°C",
        },
    }
