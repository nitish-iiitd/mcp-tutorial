from __future__ import annotations

import json

from fastmcp import FastMCP

from app.weather_service import DEFAULT_CITIES, compare_weather_data, get_current_weather_data, get_forecast_data, resolve_city

mcp = FastMCP(
    name="Weather MCP Demo",
    instructions=(
        "Use this server when the user needs current weather, a short forecast, "
        "or reusable weather-report prompts. Tools perform actions, resources expose read-only data, "
        "and prompts provide reusable templates."
    ),
)


@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """Get the current weather for a city using live Open-Meteo data."""
    return await get_current_weather_data(city)


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3) -> dict:
    """Get a daily weather forecast for a city. Days is limited to 1-7."""
    return await get_forecast_data(city, days)


@mcp.tool()
async def compare_weather(cities: list[str]) -> dict:
    """Compare current weather across up to five cities."""
    return await compare_weather_data(cities)


@mcp.resource("weather://supported-cities", mime_type="application/json")
def supported_cities() -> str:
    """Read the built-in cities available without geocoding lookup."""
    data = [
        {
            "name": item.name,
            "country": item.country,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "timezone": item.timezone,
        }
        for item in DEFAULT_CITIES.values()
    ]
    return json.dumps(data, indent=2)


@mcp.resource("weather://city/{city}/profile", mime_type="application/json")
async def city_profile(city: str) -> str:
    """Read normalized location metadata for a city."""
    location = await resolve_city(city)
    return json.dumps(
        {
            "name": location.name,
            "country": location.country,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "timezone": location.timezone,
        },
        indent=2,
    )


@mcp.resource("docs://mcp-overview", mime_type="text/markdown")
def mcp_overview() -> str:
    """Read a short internal explanation of MCP concepts."""
    return """# MCP Overview

MCP stands for Model Context Protocol. It standardizes how AI clients connect to external systems.

## Core primitives

- Tools: executable functions, such as `get_current_weather`.
- Resources: read-only context, such as `weather://supported-cities`.
- Prompts: reusable prompt templates, such as `weather_report_prompt`.

## Transport

This demo exposes MCP over Streamable HTTP at `/mcp`.
"""


@mcp.prompt()
def weather_report_prompt(city: str, audience: str = "general user") -> str:
    """Create a reusable prompt for a human-friendly weather report."""
    return (
        f"Create a clear weather report for {city}. The audience is {audience}. "
        "Mention temperature, rain risk, wind, practical advice, and any uncertainty."
    )


@mcp.prompt()
def travel_weather_advisor(city: str, days: int = 3) -> str:
    """Create a reusable prompt for travel planning around weather."""
    return (
        f"Act as a travel weather advisor for {city} for the next {days} days. "
        "Explain what to pack, best time to go out, rain precautions, and comfort tips."
    )
