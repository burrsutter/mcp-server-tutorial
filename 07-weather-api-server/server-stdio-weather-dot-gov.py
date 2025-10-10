"""
Example 7: Weather API MCP Server
Demonstrates how to integrate external REST APIs with MCP servers.
Uses weather.gov (National Weather Service) for weather data (no API key required).
"""

import asyncio
import json
import logging
from typing import Optional, Tuple
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Create the server instance
server = Server("weather-api-server")

# HTTP client for API calls
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client with required headers."""
    global http_client
    if http_client is None:
        # weather.gov requires a User-Agent header
        headers = {
            "User-Agent": "MCP-Weather-Server/1.0 (Educational Tutorial)"
        }
        http_client = httpx.AsyncClient(timeout=30.0, headers=headers)
    return http_client


async def geocode_location(location: str) -> Tuple[float, float, str]:
    """
    Convert a location name to coordinates using OpenStreetMap Nominatim.

    Args:
        location: City name or address

    Returns:
        Tuple of (latitude, longitude, display_name)
    """
    client = await get_http_client()

    # Try parsing as coordinates first (format: "lat,lon")
    if "," in location:
        try:
            parts = location.split(",")
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return (lat, lon, f"{lat},{lon}")
        except ValueError:
            pass  # Not valid coordinates, continue with geocoding

    # Geocode using Nominatim
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }

    try:
        logger.info(f"Geocoding location: {location}")
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"Location '{location}' not found")

        result = data[0]
        logger.info(f"Geocoded '{location}' to {result['display_name']} ({result['lat']}, {result['lon']})")
        return (float(result["lat"]), float(result["lon"]), result["display_name"])
    except httpx.HTTPError as e:
        logger.error(f"Geocoding failed for '{location}': {str(e)}")
        raise ValueError(f"Geocoding error: {str(e)}")


async def fetch_weather_nws(lat: float, lon: float) -> dict:
    """
    Fetch weather data from National Weather Service API.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Weather data dictionary with 'forecast' and 'gridpoint' keys
    """
    client = await get_http_client()

    try:
        # Step 1: Get the grid point data
        points_url = f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}"
        logger.info(f"Fetching NWS grid point data for coordinates: ({lat}, {lon})")
        points_response = await client.get(points_url)
        points_response.raise_for_status()
        points_data = points_response.json()
        logger.info(f"Successfully fetched grid point data for ({lat}, {lon})")

        # Step 2: Get forecast and current observations
        forecast_url = points_data["properties"]["forecast"]
        forecast_hourly_url = points_data["properties"]["forecastHourly"]

        # Fetch both forecasts
        logger.info(f"Fetching NWS forecast data from {forecast_url}")
        forecast_response = await client.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        logger.info(f"Fetching NWS hourly forecast data from {forecast_hourly_url}")
        forecast_hourly_response = await client.get(forecast_hourly_url)
        forecast_hourly_response.raise_for_status()
        hourly_data = forecast_hourly_response.json()
        logger.info(f"Successfully fetched all weather data for ({lat}, {lon})")

        return {
            "forecast": forecast_data["properties"]["periods"],
            "hourly": hourly_data["properties"]["periods"],
            "gridpoint": points_data["properties"]
        }
    except httpx.HTTPError as e:
        logger.error(f"NWS API request failed for ({lat}, {lon}): {str(e)}")
        raise ValueError(f"Weather API error: {str(e)}")
    except KeyError as e:
        logger.error(f"Unexpected NWS API response format: {str(e)}")
        raise ValueError(f"Unexpected API response format: {str(e)}")


def format_current_weather(data: dict, location_name: str) -> str:
    """Format current weather data into readable text."""
    try:
        # Use the first hourly period as "current" conditions
        current = data["hourly"][0]

        result = []
        result.append(f"📍 Location: {location_name}")
        result.append(f"🌡️  Temperature: {current['temperature']}°{current['temperatureUnit']}")
        result.append(f"🌤️  Condition: {current['shortForecast']}")
        result.append(f"💨 Wind: {current['windSpeed']} {current['windDirection']}")

        # Additional details if available
        if current.get('relativeHumidity'):
            humidity = current['relativeHumidity']['value']
            result.append(f"💧 Humidity: {humidity}%")

        if current.get('dewpoint'):
            dewpoint_c = (current['dewpoint']['value'] - 32) * 5/9
            result.append(f"💦 Dewpoint: {dewpoint_c:.1f}°C")

        result.append(f"\n📝 Detailed Forecast: {current.get('detailedForecast', 'N/A')}")

        return "\n".join(result)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Error parsing weather data: {str(e)}")


def format_forecast(data: dict, location_name: str, periods: int = 7) -> str:
    """Format weather forecast data."""
    try:
        forecast = data["forecast"][:periods * 2]  # Each day typically has 2 periods (day/night)

        result = []
        result.append(f"📍 Forecast for {location_name}\n")

        for period in forecast:
            icon = "🌙" if period.get("isDaytime") == False else "☀️"
            result.append(f"{icon} {period['name']}")
            result.append(f"   🌡️  {period['temperature']}°{period['temperatureUnit']}")
            result.append(f"   🌤️  {period['shortForecast']}")
            result.append(f"   💨 {period['windSpeed']} {period['windDirection']}")

            # Detailed forecast
            if period.get('detailedForecast'):
                result.append(f"   📝 {period['detailedForecast']}")

            result.append("")

        return "\n".join(result)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Error parsing forecast data: {str(e)}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather for a location using NWS data",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, address, or coordinates in 'lat,lon' format (e.g., 'San Francisco', 'New York', '37.7749,-122.4194')"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_weather_forecast",
            description="Get weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, address, or coordinates (lat,lon)"
                    },
                    "periods": {
                        "type": "number",
                        "description": "Number of forecast periods to show (1-14, typically 2 periods per day)",
                        "minimum": 1,
                        "maximum": 14,
                        "default": 7
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="compare_weather",
            description="Compare current weather between two locations using NWS data",
            inputSchema={
                "type": "object",
                "properties": {
                    "location1": {
                        "type": "string",
                        "description": "First location (city name, address, or coordinates)"
                    },
                    "location2": {
                        "type": "string",
                        "description": "Second location (city name, address, or coordinates)"
                    }
                },
                "required": ["location1", "location2"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""

    if name == "get_current_weather":
        location = arguments["location"]

        try:
            # Geocode location
            lat, lon, display_name = await geocode_location(location)

            # Fetch weather data
            data = await fetch_weather_nws(lat, lon)
            formatted = format_current_weather(data, display_name)
            return [TextContent(type="text", text=formatted)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]

    elif name == "get_weather_forecast":
        location = arguments["location"]
        periods = arguments.get("periods", 7)
        periods = min(max(periods, 1), 14)  # Clamp between 1 and 14

        try:
            # Geocode location
            lat, lon, display_name = await geocode_location(location)

            # Fetch weather data
            data = await fetch_weather_nws(lat, lon)
            formatted = format_forecast(data, display_name, periods)
            return [TextContent(type="text", text=formatted)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]

    elif name == "compare_weather":
        location1 = arguments["location1"]
        location2 = arguments["location2"]

        try:
            # Geocode both locations and fetch weather concurrently
            geo1_task = geocode_location(location1)
            geo2_task = geocode_location(location2)

            (lat1, lon1, name1), (lat2, lon2, name2) = await asyncio.gather(
                geo1_task, geo2_task
            )

            # Fetch weather data for both locations
            data1, data2 = await asyncio.gather(
                fetch_weather_nws(lat1, lon1),
                fetch_weather_nws(lat2, lon2)
            )

            # Extract current conditions
            curr1 = data1["hourly"][0]
            curr2 = data2["hourly"][0]

            result = []
            result.append("🌍 Weather Comparison\n")
            result.append(f"📍 {name1}")
            result.append(f"   🌡️  {curr1['temperature']}°{curr1['temperatureUnit']} - {curr1['shortForecast']}")
            result.append(f"   💨 {curr1['windSpeed']} {curr1['windDirection']}")
            result.append("")
            result.append(f"📍 {name2}")
            result.append(f"   🌡️  {curr2['temperature']}°{curr2['temperatureUnit']} - {curr2['shortForecast']}")
            result.append(f"   💨 {curr2['windSpeed']} {curr2['windDirection']}")
            result.append("")

            # Calculate difference
            temp_diff = abs(curr1['temperature'] - curr2['temperature'])
            result.append(f"📊 Temperature difference: {temp_diff}°{curr1['temperatureUnit']}")

            return [TextContent(type="text", text="\n".join(result))]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def cleanup():
    """Cleanup resources."""
    global http_client
    if http_client:
        await http_client.aclose()
        http_client = None


async def main():
    """Run the server using stdio transport."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
