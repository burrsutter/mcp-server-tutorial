"""
Example 7: Weather API MCP Server (FastMCP + HTTP)
Demonstrates how to integrate external REST APIs with MCP servers.
Uses Open-Meteo API for weather data (no API key required).
Runs on HTTP transport on port 9003.
"""

import asyncio
import logging
from typing import Optional, Tuple
import httpx
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Create the FastMCP server instance
mcp = FastMCP("weather-api-server")

# HTTP client for API calls
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=30.0)
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
    headers = {
        "User-Agent": "MCP-Weather-Server/1.0 (Educational Tutorial)"
    }

    try:
        logger.info(f"Geocoding location: {location}")
        response = await client.get(url, params=params, headers=headers)
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


def get_weather_description(code: int) -> str:
    """Convert Open-Meteo weather code to description."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, f"Unknown ({code})")


def degrees_to_cardinal(degrees: float) -> str:
    """Convert wind direction degrees to cardinal direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


async def fetch_weather_open_meteo(lat: float, lon: float) -> dict:
    """
    Fetch weather data from Open-Meteo API.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Weather data dictionary with 'current', 'hourly', and 'daily' keys
    """
    client = await get_http_client()

    try:
        # Open-Meteo API endpoint
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature",
                       "precipitation", "weather_code", "wind_speed_10m", "wind_direction_10m"],
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability",
                      "weather_code", "wind_speed_10m", "wind_direction_10m"],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min",
                     "precipitation_probability_max", "wind_speed_10m_max"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "auto"
        }

        logger.info(f"Fetching weather data for coordinates: ({lat}, {lon})")
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched weather data for ({lat}, {lon})")

        return data
    except httpx.HTTPError as e:
        logger.error(f"Weather API request failed for ({lat}, {lon}): {str(e)}")
        raise ValueError(f"Weather API error: {str(e)}")
    except KeyError as e:
        logger.error(f"Unexpected weather API response format: {str(e)}")
        raise ValueError(f"Unexpected API response format: {str(e)}")


def format_current_weather(data: dict, location_name: str) -> str:
    """Format current weather data into readable text."""
    try:
        current = data["current"]
        current_units = data.get("current_units", {})

        result = []
        result.append(f"📍 Location: {location_name}")
        result.append(f"🕐 Time: {current['time']}")

        # Temperature
        temp = current['temperature_2m']
        temp_unit = current_units.get('temperature_2m', '°F')
        result.append(f"🌡️  Temperature: {temp}{temp_unit}")

        # Feels like
        if 'apparent_temperature' in current:
            feels_like = current['apparent_temperature']
            result.append(f"🌡️  Feels like: {feels_like}{temp_unit}")

        # Weather condition
        weather_code = current.get('weather_code', 0)
        condition = get_weather_description(weather_code)
        result.append(f"🌤️  Condition: {condition}")

        # Wind
        wind_speed = current.get('wind_speed_10m', 0)
        wind_dir = current.get('wind_direction_10m', 0)
        wind_cardinal = degrees_to_cardinal(wind_dir)
        wind_unit = current_units.get('wind_speed_10m', 'mph')
        result.append(f"💨 Wind: {wind_speed} {wind_unit} {wind_cardinal}")

        # Humidity
        if 'relative_humidity_2m' in current:
            humidity = current['relative_humidity_2m']
            result.append(f"💧 Humidity: {humidity}%")

        # Precipitation
        if 'precipitation' in current and current['precipitation'] > 0:
            precip = current['precipitation']
            precip_unit = current_units.get('precipitation', 'in')
            result.append(f"🌧️  Precipitation: {precip} {precip_unit}")

        return "\n".join(result)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Error parsing weather data: {str(e)}")


def format_forecast(data: dict, location_name: str, periods: int = 7) -> str:
    """Format weather forecast data."""
    try:
        daily = data["daily"]
        daily_units = data.get("daily_units", {})

        # Limit to requested periods
        num_days = min(periods, len(daily["time"]))

        result = []
        result.append(f"📍 {num_days}-Day Forecast for {location_name}\n")

        for i in range(num_days):
            date = daily["time"][i]
            temp_max = daily["temperature_2m_max"][i]
            temp_min = daily["temperature_2m_min"][i]
            weather_code = daily["weather_code"][i]
            condition = get_weather_description(weather_code)

            temp_unit = daily_units.get('temperature_2m_max', '°F')

            result.append(f"📅 {date}")
            result.append(f"   🌡️  High: {temp_max}{temp_unit} / Low: {temp_min}{temp_unit}")
            result.append(f"   🌤️  {condition}")

            # Precipitation probability
            if "precipitation_probability_max" in daily:
                precip_prob = daily["precipitation_probability_max"][i]
                if precip_prob > 0:
                    result.append(f"   💧 Precipitation: {precip_prob}%")

            # Wind
            if "wind_speed_10m_max" in daily:
                wind_max = daily["wind_speed_10m_max"][i]
                wind_unit = daily_units.get('wind_speed_10m_max', 'mph')
                result.append(f"   💨 Max wind: {wind_max} {wind_unit}")

            result.append("")

        return "\n".join(result)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Error parsing forecast data: {str(e)}")


@mcp.tool()
async def get_current_weather(location: str) -> str:
    """
    Get current weather for a location using Open-Meteo API.

    Args:
        location: City name, address, or coordinates in 'lat,lon' format
                 (e.g., 'San Francisco', 'New York', '37.7749,-122.4194')

    Returns:
        Formatted current weather information
    """
    try:
        # Geocode location
        lat, lon, display_name = await geocode_location(location)

        # Fetch weather data
        data = await fetch_weather_open_meteo(lat, lon)
        formatted = format_current_weather(data, display_name)
        return formatted
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def get_weather_forecast(location: str, periods: int = 7) -> str:
    """
    Get multi-day weather forecast for a location using Open-Meteo API.

    Args:
        location: City name, address, or coordinates (lat,lon)
        periods: Number of days to forecast (1-14), defaults to 7

    Returns:
        Formatted weather forecast information
    """
    # Clamp between 1 and 14
    periods = min(max(periods, 1), 14)

    try:
        # Geocode location
        lat, lon, display_name = await geocode_location(location)

        # Fetch weather data
        data = await fetch_weather_open_meteo(lat, lon)
        formatted = format_forecast(data, display_name, periods)
        return formatted
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def compare_weather(location1: str, location2: str) -> str:
    """
    Compare current weather between two locations using Open-Meteo API.

    Args:
        location1: First location (city name, address, or coordinates)
        location2: Second location (city name, address, or coordinates)

    Returns:
        Comparison of weather conditions between the two locations
    """
    try:
        # Geocode both locations and fetch weather concurrently
        geo1_task = geocode_location(location1)
        geo2_task = geocode_location(location2)

        (lat1, lon1, name1), (lat2, lon2, name2) = await asyncio.gather(
            geo1_task, geo2_task
        )

        # Fetch weather data for both locations
        data1, data2 = await asyncio.gather(
            fetch_weather_open_meteo(lat1, lon1),
            fetch_weather_open_meteo(lat2, lon2)
        )

        # Extract current conditions
        curr1 = data1["current"]
        curr2 = data2["current"]
        units = data1.get("current_units", {})

        # Get weather descriptions
        condition1 = get_weather_description(curr1.get('weather_code', 0))
        condition2 = get_weather_description(curr2.get('weather_code', 0))

        # Get wind directions
        wind_dir1 = degrees_to_cardinal(curr1.get('wind_direction_10m', 0))
        wind_dir2 = degrees_to_cardinal(curr2.get('wind_direction_10m', 0))

        temp_unit = units.get('temperature_2m', '°F')
        wind_unit = units.get('wind_speed_10m', 'mph')

        result = []
        result.append("🌍 Weather Comparison\n")
        result.append(f"📍 {name1}")
        result.append(f"   🌡️  {curr1['temperature_2m']}{temp_unit} - {condition1}")
        result.append(f"   💨 {curr1['wind_speed_10m']} {wind_unit} {wind_dir1}")
        if 'relative_humidity_2m' in curr1:
            result.append(f"   💧 {curr1['relative_humidity_2m']}%")
        result.append("")
        result.append(f"📍 {name2}")
        result.append(f"   🌡️  {curr2['temperature_2m']}{temp_unit} - {condition2}")
        result.append(f"   💨 {curr2['wind_speed_10m']} {wind_unit} {wind_dir2}")
        if 'relative_humidity_2m' in curr2:
            result.append(f"   💧 {curr2['relative_humidity_2m']}%")
        result.append("")

        # Calculate difference
        temp_diff = abs(curr1['temperature_2m'] - curr2['temperature_2m'])
        result.append(f"📊 Temperature difference: {temp_diff:.1f}{temp_unit}")

        return "\n".join(result)
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


async def cleanup():
    """Cleanup resources."""
    global http_client
    if http_client:
        await http_client.aclose()
        http_client = None


if __name__ == "__main__":
    # Run the server using HTTP transport on port 9003
    try:
        mcp.run(transport="http", port=9003, host="0.0.0.0")
    finally:
        asyncio.run(cleanup())
