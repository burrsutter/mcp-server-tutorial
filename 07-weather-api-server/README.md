# Example 7: Weather API MCP Server

This example demonstrates how to integrate external REST APIs with MCP servers. It uses the free wttr.in weather API to provide weather information through MCP tools.

## What This Example Demonstrates

- Making HTTP REST API calls from MCP tools
- Using `httpx` for async HTTP requests
- Error handling for API calls
- Data parsing and formatting
- Concurrent API requests with `asyncio.gather`
- Resource cleanup
- No API key requirements (uses free API)

## Files

- `server.py` - Weather API MCP server
- `requirements.txt` - Python dependencies (includes httpx)

## Features

### Tools

1. **get_current_weather**
   - Get current weather for any location
   - Supports city names and coordinates
   - Returns temperature, conditions, wind, humidity, etc.

2. **get_weather_forecast**
   - Get 1-3 day forecast for a location
   - Daily highs/lows
   - Weather conditions and precipitation chances

3. **compare_weather**
   - Compare weather between two locations
   - Shows temperature difference
   - Concurrent API calls for efficiency

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### With a Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_weather():
    server_params = StdioServerParameters(
        command="python",
        args=["../07-weather-api-server/server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get current weather
            result = await session.call_tool(
                "get_current_weather",
                arguments={"location": "London"}
            )
            print(result.content[0].text)
            
            # Get forecast
            result = await session.call_tool(
                "get_weather_forecast",
                arguments={"location": "New York", "days": 3}
            )
            print(result.content[0].text)
            
            # Compare weather
            result = await session.call_tool(
                "compare_weather",
                arguments={"location1": "Tokyo", "location2": "Paris"}
            )
            print(result.content[0].text)
```

## Example Output

### Current Weather
```
📍 Location: London, United Kingdom
🌡️  Temperature: 15°C (59°F)
🌤️  Condition: Partly cloudy
💨 Wind: 20 km/h WSW
💧 Humidity: 72%
👁️  Visibility: 10 km
☁️  Cloud Cover: 50%
```

### Forecast
```
📍 3-Day Forecast for New York, United States

📅 2024-01-15
   🌡️  Max: 8°C / Min: 2°C
   🌤️  Sunny
   💧 Humidity: 65%
   🌧️  Chance of Rain: 10%

📅 2024-01-16
   🌡️  Max: 10°C / Min: 4°C
   🌤️  Partly cloudy
   💧 Humidity: 70%
   🌧️  Chance of Rain: 20%
...
```

## Key Concepts

### HTTP Client Management
```python
http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=30.0)
    return http_client
```
Reuse HTTP client across requests for efficiency.

### Async API Calls
```python
async def fetch_weather_wttr(location: str) -> dict:
    client = await get_http_client()
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

### Concurrent Requests
```python
# Fetch multiple locations at once
data1, data2 = await asyncio.gather(
    fetch_weather_wttr(location1),
    fetch_weather_wttr(location2)
)
```

### Error Handling
```python
try:
    data = await fetch_weather_wttr(location)
    formatted = format_current_weather(data)
    return [TextContent(type="text", text=formatted)]
except ValueError as e:
    return [TextContent(type="text", text=f"Error: {str(e)}")]
except Exception as e:
    return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]
```

### Resource Cleanup
```python
async def cleanup():
    global http_client
    if http_client:
        await http_client.aclose()
        http_client = None

async def main():
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(...)
    finally:
        await cleanup()
```

## About wttr.in API

This example uses [wttr.in](https://wttr.in/), a free weather API that:
- Requires no API key
- Supports multiple formats
- Provides detailed weather data
- Has reasonable rate limits for testing

For production use, consider:
- OpenWeatherMap API
- WeatherAPI
- Other commercial weather services

## Adapting for Other APIs

To use a different weather API:

1. Update the API endpoint:
```python
url = "https://api.yourservice.com/weather"
```

2. Add API key handling:
```python
API_KEY = os.environ.get("WEATHER_API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}
response = await client.get(url, headers=headers)
```

3. Update data parsing:
```python
def format_current_weather(data: dict) -> str:
    # Parse based on your API's response format
    temp = data["main"]["temp"]
    ...
```

## Extension Ideas

Add more tools:
- Weather alerts
- Historical weather data
- Air quality index
- UV index
- Sunrise/sunset times
- Moon phases
- Marine weather
- Weather maps

## Best Practices

1. **Connection Pooling**: Reuse HTTP clients
2. **Timeouts**: Always set request timeouts
3. **Error Handling**: Handle API errors gracefully
4. **Rate Limiting**: Respect API rate limits
5. **Caching**: Cache responses when appropriate
6. **Data Validation**: Validate API responses
7. **Resource Cleanup**: Close connections properly

## Troubleshooting

**Connection Errors**
- Check internet connection
- Verify API endpoint is accessible
- Check firewall settings

**API Errors**
- Verify location spelling
- Check API status
- Review rate limits

**Parsing Errors**
- API response format may have changed
- Location not found
- Update parsing logic

## Next Steps

- See Example 8 for FastAPI + MCP integration
- See Example 9 for Kubernetes deployment
- Add your own external API integrations
- Implement caching for better performance
