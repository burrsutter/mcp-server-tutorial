#!/usr/bin/env python3
"""
Test script to demonstrate divide by zero error handling
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Test the divide tool with normal division and division by zero."""

    # Define server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["./01-simple-server/server-stdio-math.py"],
    )

    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            print("Connected to MCP Math Server!\n")

            # Test 1: Normal division
            print("=== Test 1: Normal Division ===")
            print("Dividing 100 by 5")
            result1 = await session.call_tool(
                "divide",
                arguments={"a": 100, "b": 5}
            )
            response1 = json.loads(result1.content[0].text)
            print(f"Result: {response1}")
            print()

            # Test 2: Division by zero
            print("=== Test 2: Division by Zero ===")
            print("Dividing 100 by 0 (should trigger error)")
            result2 = await session.call_tool(
                "divide",
                arguments={"a": 100, "b": 0}
            )
            response2 = json.loads(result2.content[0].text)

            if "error" in response2:
                print(f"Error caught: {response2['error']}")
            else:
                print(f"Result: {response2}")
            print()

            # Test 3: Decimal division
            print("=== Test 3: Decimal Division ===")
            print("Dividing 7 by 2")
            result3 = await session.call_tool(
                "divide",
                arguments={"a": 7, "b": 2}
            )
            response3 = json.loads(result3.content[0].text)
            print(f"Result: {response3}")


if __name__ == "__main__":
    asyncio.run(main())
