#!/usr/bin/env python3
"""
Example 2: Simplest MCP Client
A minimal MCP client that connects to a server and calls tools.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Main client function demonstrating basic MCP client operations."""
    
    # Define server parameters - path to the server script
    server_params = StdioServerParameters(
        command="python",
        args=["./01-simple-server/server-stdio-echo.py"],
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
            
            # Call the echo tool
            print("=== Calling the 'echo' Tool ===")
            result = await session.call_tool(
                "echo",
                arguments={"message": "Hello from the MCP client!"}
            )
            
            print(f"Result: {result.content[0].text}")
            
            print("\n" + "="*50 + "\n")
            
            # Try another echo with different message
            print("=== Calling 'echo' Again ===")
            result2 = await session.call_tool(
                "echo",
                arguments={"message": "MCP is working!"}
            )
            
            print(f"Result: {result2.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
