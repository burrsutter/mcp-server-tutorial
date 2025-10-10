#!/usr/bin/env python3
"""
Example 1: MCP Math Server
A simple MCP server with basic math operations (add, subtract, multiply, divide).
"""

import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create the server instance
server = Server("simple-math-server")


# Define available tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="add",
            description="Adds two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="subtract",
            description="Subtracts the second number from the first",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiply",
            description="Multiplies two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="divide",
            description="Divides the first number by the second",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Numerator"
                    },
                    "b": {
                        "type": "number",
                        "description": "Denominator"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]


# Handle tool execution
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""
    if name == "add":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return [TextContent(
            type="text",
            text=json.dumps({"result": result})
        )]

    elif name == "subtract":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a - b
        return [TextContent(
            type="text",
            text=json.dumps({"result": result})
        )]

    elif name == "multiply":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a * b
        return [TextContent(
            type="text",
            text=json.dumps({"result": result})
        )]

    elif name == "divide":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)

        # Check for division by zero
        if b == 0:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "Cannot divide by zero"})
            )]

        result = a / b
        return [TextContent(
            type="text",
            text=json.dumps({"result": result})
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
