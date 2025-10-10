#!/usr/bin/env python3
"""
MCP Server Wrapper for FastAPI - Kubernetes Version
Wraps the Task Manager FastAPI application with MCP protocol in Kubernetes.
"""

import asyncio
import json
import os
from typing import Optional
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, TextContent


# Create the server instance
server = Server("task-manager-mcp")

# Configuration - Use Kubernetes service name
API_BASE_URL = os.environ.get("FASTAPI_URL", "http://fastapi-service:8000")
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0)
    return http_client


async def api_request(method: str, endpoint: str, **kwargs) -> dict:
    """Make an API request to the FastAPI backend."""
    client = await get_http_client()
    
    try:
        response = await client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        raise ValueError(f"API Error ({e.response.status_code}): {error_detail}")
    except httpx.HTTPError as e:
        raise ValueError(f"HTTP Error: {str(e)}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="create_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description (optional)"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks, optionally filtered by completion status",
            inputSchema={
                "type": "object",
                "properties": {
                    "completed": {"type": "boolean", "description": "Filter by completion status (optional)"}
                }
            }
        ),
        Tool(
            name="get_task",
            description="Get a specific task by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "number", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "number", "description": "Task ID"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "completed": {"type": "boolean", "description": "Completion status (optional)"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "number", "description": "Task ID to delete"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="get_task_stats",
            description="Get task statistics",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""
    
    try:
        if name == "create_task":
            data = {"title": arguments["title"], "description": arguments.get("description")}
            result = await api_request("POST", "/tasks", json=data)
            return [TextContent(
                type="text",
                text=f"✅ Task created successfully!\n\nID: {result['id']}\nTitle: {result['title']}\nDescription: {result.get('description', 'None')}\nStatus: {'Completed' if result['completed'] else 'Pending'}"
            )]
        
        elif name == "list_tasks":
            params = {}
            if "completed" in arguments:
                params["completed"] = arguments["completed"]
            result = await api_request("GET", "/tasks", params=params)
            
            if not result:
                return [TextContent(type="text", text="No tasks found.")]
            
            task_list = [f"{'✅' if task['completed'] else '⏳'} ID: {task['id']} - {task['title']}" for task in result]
            return [TextContent(type="text", text=f"Found {len(result)} task(s):\n\n" + "\n".join(task_list))]
        
        elif name == "get_task":
            task_id = int(arguments["task_id"])
            result = await api_request("GET", f"/tasks/{task_id}")
            return [TextContent(
                type="text",
                text=f"📋 Task Details\n\nID: {result['id']}\nTitle: {result['title']}\nDescription: {result.get('description', 'None')}\nStatus: {'✅ Completed' if result['completed'] else '⏳ Pending'}\nCreated: {result['created_at']}\nUpdated: {result['updated_at']}"
            )]
        
        elif name == "update_task":
            task_id = int(arguments["task_id"])
            data = {}
            if "title" in arguments:
                data["title"] = arguments["title"]
            if "description" in arguments:
                data["description"] = arguments["description"]
            if "completed" in arguments:
                data["completed"] = arguments["completed"]
            
            result = await api_request("PUT", f"/tasks/{task_id}", json=data)
            return [TextContent(
                type="text",
                text=f"✅ Task updated successfully!\n\nID: {result['id']}\nTitle: {result['title']}\nDescription: {result.get('description', 'None')}\nStatus: {'✅ Completed' if result['completed'] else '⏳ Pending'}\nLast updated: {result['updated_at']}"
            )]
        
        elif name == "delete_task":
            task_id = int(arguments["task_id"])
            result = await api_request("DELETE", f"/tasks/{task_id}")
            return [TextContent(type="text", text=f"🗑️ Task deleted: {result['task']['title']}")]
        
        elif name == "get_task_stats":
            result = await api_request("GET", "/stats")
            return [TextContent(
                type="text",
                text=f"📊 Task Statistics\n\nTotal Tasks: {result['total_tasks']}\nCompleted: {result['completed_tasks']}\nPending: {result['pending_tasks']}\nCompletion Rate: {result['completion_rate']}"
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except ValueError as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Unexpected error: {str(e)}")]


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="tasks://all",
            name="All Tasks",
            mimeType="application/json",
            description="Complete list of all tasks as JSON"
        ),
        Resource(
            uri="tasks://stats",
            name="Task Statistics",
            mimeType="application/json",
            description="Task statistics and metrics"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    try:
        if uri == "tasks://all":
            result = await api_request("GET", "/tasks")
            return json.dumps(result, indent=2)
        elif uri == "tasks://stats":
            result = await api_request("GET", "/stats")
            return json.dumps(result, indent=2)
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    except ValueError as e:
        raise ValueError(f"Error reading resource: {str(e)}")


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
