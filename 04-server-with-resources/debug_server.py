#!/usr/bin/env python3
"""
Debug script for MCP server TaskGroup errors.
This script helps identify the specific cause of async TaskGroup issues.
"""

import asyncio
import sys
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def debug_server():
    """Debug the MCP server to identify TaskGroup issues."""
    server_params = StdioServerParameters(
        command="python",
        args=["./mcp-server-resources.py"],
    )

    print("🔍 Starting MCP server debug session...")
    print("=" * 60)
    
    try:
        async with stdio_client(server_params) as (read, write):
            print("✅ Server connection established")
            
            async with ClientSession(read, write) as session:
                print("✅ Client session created")
                
                # Test initialization
                print("🔄 Initializing session...")
                await session.initialize()
                print("✅ Session initialized successfully")
                
                # Test resource listing
                print("🔄 Listing resources...")
                resources = await session.list_resources()
                print(f"✅ Found {len(resources.resources)} resources")
                
                # Test resource templates
                print("🔄 Listing resource templates...")
                templates = await session.list_resource_templates()
                print(f"✅ Found {len(templates.resourceTemplates)} templates")
                
                # Test reading a resource
                print("🔄 Reading static resource...")
                content = await session.read_resource("note://static/welcome")
                print("✅ Static resource read successfully")
                
                # Test reading dynamic resource
                print("🔄 Reading dynamic resource...")
                note = await session.read_resource("note://notes/note1")
                print("✅ Dynamic resource read successfully")
                
                print("\n" + "=" * 60)
                print("🎉 All tests passed! No TaskGroup errors detected.")
                print("=" * 60)
                
    except asyncio.CancelledError:
        print("\n⚠️  Debug session cancelled")
        raise
    except Exception as e:
        print(f"\n❌ Debug error: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        
        # Additional debugging info
        print("\n🔍 Additional debugging information:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception args: {e.args}")
        
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"Caused by: {e.__cause__}")
        
        raise


if __name__ == "__main__":
    try:
        asyncio.run(debug_server())
    except KeyboardInterrupt:
        print("\n🛑 Debug session interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error in debug session: {e}")
        sys.exit(1)
