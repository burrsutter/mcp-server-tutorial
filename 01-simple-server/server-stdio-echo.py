#!/usr/bin/env python3
"""
Example 1: Simplest MCP Server
A minimal MCP server with a single 'echo' tool that demonstrates the basic structure.
"""

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create the server instance
server = Server("simple-echo-server")


# Define available tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="echo",
            description="Echoes back the input text",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
    ]


# Handle tool execution
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""
    if name == "echo":
        message = arguments.get("message", "")
        return [TextContent(
            type="text",
            text=f"Echo: {message}"
        )]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
