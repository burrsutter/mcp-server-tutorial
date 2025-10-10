# Example 8: FastAPI + MCP Wrapper

This example demonstrates how to wrap an existing FastAPI REST API with an MCP server, making it accessible through the MCP protocol. This pattern is useful for integrating existing services with MCP-enabled applications.

## What This Example Demonstrates

- Wrapping a REST API with MCP
- Two-service architecture (FastAPI + MCP)
- HTTP-based tool implementation
- Bidirectional communication patterns
- Resource exposure from REST APIs
- Error handling across service boundaries

## Components

### 1. FastAPI Application (`fastapi_app.py`)
A simple task management REST API with:
- CRUD operations for tasks
- Task filtering and statistics
- OpenAPI documentation
- Pydantic models for validation

### 2. MCP Server (`mcp_server.py`)
An MCP wrapper that:
- Translates MCP tool calls to REST API requests
- Exposes API endpoints as MCP tools
- Provides resources for data access
- Handles errors from both layers

## Architecture

```
MCP Client
    ↓
MCP Server (mcp_server.py)
    ↓ HTTP
FastAPI Application (fastapi_app.py)
    ↓
In-Memory Data Store
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the System

### Step 1: Start the FastAPI Backend

In terminal 1:
```bash
python fastapi_app.py
```

The API will be available at:
- Main API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

### Step 2: Use the MCP Server

In terminal 2, you can either:

**Option A: Run with a test client**
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def demo():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create a task
            result = await session.call_tool(
                "create_task",
                arguments={
                    "title": "Learn MCP",
                    "description": "Complete the MCP tutorial"
                }
            )
            print(result.content[0].text)
```

**Option B: Test FastAPI directly**
```bash
curl http://localhost:8000/tasks
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Testing"}'
```

## Available Tools

### create_task
Create a new task.
- **Parameters**: 
  - `title` (string, required)
  - `description` (string, optional)

### list_tasks
List all tasks, optionally filtered.
- **Parameters**:
  - `completed` (boolean, optional) - Filter by completion status

### get_task
Get a specific task by ID.
- **Parameters**:
  - `task_id` (number, required)

### update_task
Update an existing task.
- **Parameters**:
  - `task_id` (number, required)
  - `title` (string, optional)
  - `description` (string, optional)
  - `completed` (boolean, optional)

### delete_task
Delete a task.
- **Parameters**:
  - `task_id` (number, required)

### get_task_stats
Get task statistics.
- **Parameters**: None

## Available Resources

### tasks://all
Complete list of all tasks as JSON

### tasks://stats
Task statistics and metrics as JSON

## Key Concepts

### REST API Wrapping Pattern

The MCP server acts as an adapter:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "create_task":
        # Translate MCP arguments to REST API request
        data = {
            "title": arguments["title"],
            "description": arguments.get("description")
        }
        result = await api_request("POST", "/tasks", json=data)
        
        # Format response for MCP
        return [TextContent(type="text", text=format_result(result))]
```

### HTTP Client Management

```python
http_client = httpx.AsyncClient(
    base_url="http://localhost:8000",
    timeout=10.0
)
```

Reuse the client across requests for connection pooling.

### Error Translation

```python
except httpx.HTTPStatusError as e:
    # Extract error from FastAPI response
    error_detail = e.response.json().get("detail", str(e))
    raise ValueError(f"API Error ({e.response.status_code}): {error_detail}")
```

Convert HTTP errors to MCP-friendly format.

### Two-Way Communication

1. **MCP → REST**: Tools call REST endpoints
2. **REST → MCP**: Resources expose REST data

## Why Use This Pattern?

### Benefits

1. **Reuse Existing APIs**: Don't rewrite working REST APIs
2. **Separation of Concerns**: API logic separate from MCP protocol
3. **Independent Scaling**: Scale API and MCP server independently
4. **Multiple Clients**: REST API remains accessible to other clients
5. **Testing**: Test API and MCP layer separately

### When to Use

- Integrating existing services
- Microservices architecture
- When API and MCP have different lifecycles
- Need for independent deployment

### When NOT to Use

- Simple, standalone applications
- Performance-critical paths (adds HTTP overhead)
- When you control both ends and can use direct integration

## Testing

### Test the FastAPI API
```bash
# List tasks
curl http://localhost:8000/tasks

# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Description"}'

# Get task
curl http://localhost:8000/tasks/1

# Update task
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete task
curl -X DELETE http://localhost:8000/tasks/1

# Get stats
curl http://localhost:8000/stats
```

### Test the MCP Server
Use Example 2's client pattern, modified to point to this server.

## Extending the Example

### Add Authentication
```python
# In MCP server
API_KEY = os.environ.get("API_KEY")
http_client = httpx.AsyncClient(
    base_url=API_BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"}
)
```

### Add Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

cache = {}
cache_duration = timedelta(minutes=5)

async def api_request_with_cache(method, endpoint, **kwargs):
    if method == "GET":
        key = f"{endpoint}:{kwargs}"
        if key in cache:
            data, timestamp = cache[key]
            if datetime.now() - timestamp < cache_duration:
                return data
    
    result = await api_request(method, endpoint, **kwargs)
    
    if method == "GET":
        cache[key] = (result, datetime.now())
    
    return result
```

### Add Rate Limiting
```python
from asyncio import Semaphore

rate_limiter = Semaphore(10)  # Max 10 concurrent requests

async def api_request(method, endpoint, **kwargs):
    async with rate_limiter:
        # Make request
        ...
```

## Production Considerations

1. **Service Discovery**: Use environment variables for API_BASE_URL
2. **Health Checks**: Add health check endpoints
3. **Logging**: Add structured logging for debugging
4. **Metrics**: Track API response times and errors
5. **Retries**: Implement retry logic for transient failures
6. **Circuit Breakers**: Prevent cascade failures
7. **Authentication**: Add proper auth for production
8. **HTTPS**: Use HTTPS in production

## Troubleshooting

**MCP Server Can't Connect to API**
- Ensure FastAPI is running on localhost:8000
- Check firewall settings
- Verify API_BASE_URL is correct

**Timeout Errors**
- Increase httpx timeout
- Check API performance
- Add retry logic

**Data Inconsistencies**
- Clear in-memory storage (restart FastAPI)
- Check for race conditions
- Add proper locking if needed

## Next Steps

- See Example 9 for Kubernetes deployment of this system
- Add database persistence to FastAPI
- Implement WebSocket support
- Add real-time updates
- Create a web UI for the task manager
