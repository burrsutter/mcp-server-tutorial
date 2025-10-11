#!/usr/bin/env python3
"""
Example 8: MCP Server Wrapper for FastAPI (FastMCP + HTTP)
Wraps the Task Manager FastAPI application with MCP protocol.
Makes REST API accessible through MCP tools via HTTP on port 9004.
"""

import json
from typing import Optional
import httpx
from fastmcp import FastMCP

# Create the FastMCP server instance
mcp = FastMCP("task-manager-mcp")

# Configuration
API_BASE_URL = "http://localhost:8000"
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0)
    return http_client


async def api_request(method: str, endpoint: str, **kwargs) -> dict:
    """
    Make an API request to the FastAPI backend.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path
        **kwargs: Additional arguments for httpx request

    Returns:
        JSON response data
    """
    client = await get_http_client()

    try:
        response = await client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # Extract error detail from response if available
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        raise ValueError(f"API Error ({e.response.status_code}): {error_detail}")
    except httpx.HTTPError as e:
        raise ValueError(f"HTTP Error: {str(e)}")


# Tools
@mcp.tool()
async def create_task(title: str, description: str = None) -> str:
    """Create a new task

    Args:
        title: Task title
        description: Task description (optional)
    """
    data = {
        "title": title,
        "description": description
    }
    result = await api_request("POST", "/tasks", json=data)

    return (f"✅ Task created successfully!\n\n"
            f"ID: {result['id']}\n"
            f"Title: {result['title']}\n"
            f"Description: {result.get('description', 'None')}\n"
            f"Status: {'Completed' if result['completed'] else 'Pending'}")


@mcp.tool()
async def list_tasks(completed: Optional[bool] = None) -> str:
    """List all tasks, optionally filtered by completion status

    Args:
        completed: Filter by completion status (optional)
    """
    params = {}
    if completed is not None:
        params["completed"] = completed

    result = await api_request("GET", "/tasks", params=params)

    if not result:
        return "No tasks found."

    task_list = []
    for task in result:
        status = "✅" if task["completed"] else "⏳"
        task_list.append(
            f"{status} ID: {task['id']} - {task['title']}"
        )

    return f"Found {len(result)} task(s):\n\n" + "\n".join(task_list)


@mcp.tool()
async def get_task(task_id: int) -> str:
    """Get a specific task by ID

    Args:
        task_id: Task ID
    """
    result = await api_request("GET", f"/tasks/{task_id}")

    return (f"📋 Task Details\n\n"
            f"ID: {result['id']}\n"
            f"Title: {result['title']}\n"
            f"Description: {result.get('description', 'None')}\n"
            f"Status: {'✅ Completed' if result['completed'] else '⏳ Pending'}\n"
            f"Created: {result['created_at']}\n"
            f"Updated: {result['updated_at']}")


@mcp.tool()
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> str:
    """Update an existing task

    Args:
        task_id: Task ID
        title: New title (optional)
        description: New description (optional)
        completed: Completion status (optional)
    """
    data = {}
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if completed is not None:
        data["completed"] = completed

    result = await api_request("PUT", f"/tasks/{task_id}", json=data)

    return (f"✅ Task updated successfully!\n\n"
            f"ID: {result['id']}\n"
            f"Title: {result['title']}\n"
            f"Description: {result.get('description', 'None')}\n"
            f"Status: {'✅ Completed' if result['completed'] else '⏳ Pending'}\n"
            f"Last updated: {result['updated_at']}")


@mcp.tool()
async def delete_task(task_id: int) -> str:
    """Delete a task

    Args:
        task_id: Task ID to delete
    """
    result = await api_request("DELETE", f"/tasks/{task_id}")
    return f"🗑️ Task deleted: {result['task']['title']}"


@mcp.tool()
async def get_task_stats() -> str:
    """Get task statistics"""
    result = await api_request("GET", "/stats")

    return (f"📊 Task Statistics\n\n"
            f"Total Tasks: {result['total_tasks']}\n"
            f"Completed: {result['completed_tasks']}\n"
            f"Pending: {result['pending_tasks']}\n"
            f"Completion Rate: {result['completion_rate']}")


# Resources
@mcp.resource("tasks://all")
async def get_all_tasks() -> str:
    """Complete list of all tasks as JSON"""
    result = await api_request("GET", "/tasks")
    return json.dumps(result, indent=2)


@mcp.resource("tasks://stats")
async def get_stats() -> str:
    """Task statistics and metrics"""
    result = await api_request("GET", "/stats")
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Run the server with HTTP transport on port 9004
    # Configure to expose REST endpoints at /mcp/v1/
    mcp.run(transport="http", port=9004, path="/mcp/v1/")
