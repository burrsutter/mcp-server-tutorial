#!/usr/bin/env python3
"""
Example 2: Simplest MCP Client
A minimal MCP client that connects to a server and calls tools.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Main client function demonstrating basic MCP client operations."""
    
    # Define server parameters - path to the server script
    server_params = StdioServerParameters(
        command="python",
        args=["./01-simple-server/server-stdio-math.py"],
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("Connected to MCP server!\n")
            
            # List available tools
            print("=== Listing Available Tools ===")
            tools_response = await session.list_tools()
            
            for tool in tools_response.tools:
                print(f"\nTool: {tool.name}")
                print(f"Description: {tool.description}")
                print(f"Input Schema: {tool.inputSchema}")
            
            print("\n" + "="*50 + "\n")
            
            a = 10
            b = 5
            # Call the add tool
            print("=== Calling the 'add' Tool ===")
            result = await session.call_tool(
                "add",
                arguments={"a": a, "b": b}
            )
            
            print(f"Result: {result.content[0].text}")

            # Extract the result from add to use in subtract
            result_data = json.loads(result.content[0].text)
            y = int(result_data["result"])

            print("\n" + "="*50 + "\n")

            # Call the subtract tool using the result from add
            x = 100
            print("=== Calling the 'subtract' Tool ===")
            print(f"Subtracting {y} (from add result) from {x}")
            result2 = await session.call_tool(
                "subtract",
                arguments={"a": x, "b": y}
            )

            
            
            print(f"Result: {result2.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
