#!/usr/bin/env python3
"""
Client example for testing MCP server resources.
Demonstrates listing and reading both static and dynamic resources.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Resource, ResourceTemplate, TextContent



async def test_resources():
    """Test the MCP resource server capabilities."""
    server_params = StdioServerParameters(
        command="python",
        args=["./04-server-with-resources/mcp-server-resources.py"],
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # List all resources
                print("\n" + "=" * 50)
                print("AVAILABLE RESOURCES")
                print("=" * 50)
                resources = await session.list_resources()
                for res in resources.resources:
                    print(f"\n  📄 {res.name}")
                    print(f"     URI: {res.uri}")
                    print(f"     Type: {res.mimeType}")
                    print(f"     Description: {res.description}")

                # List resource templates
                print("\n" + "=" * 50)
                print("RESOURCE TEMPLATES")
                print("=" * 50)
                templates = await session.list_resource_templates()
                for tmpl in templates.resourceTemplates:
                    print(f"\n  📋 {tmpl.name}")
                    print(f"     URI Pattern: {tmpl.uriTemplate}")
                    print(f"     Type: {tmpl.mimeType}")
                    print(f"     Description: {tmpl.description}")

                # Read a static resource
                print("\n" + "=" * 50)
                print("READING: note://static/welcome")
                print("=" * 50)
                content = await session.read_resource("note://static/welcome")
                print(content.contents[0].text)

                # Read another static resource (JSON)
                print("\n" + "=" * 50)
                print("READING: note://static/info")
                print("=" * 50)
                info = await session.read_resource("note://static/info")
                print(info.contents[0].text)

                # Read a dynamic resource
                print("\n" + "=" * 50)
                print("READING: note://notes/note1")
                print("=" * 50)
                note = await session.read_resource("note://notes/note1")
                print(note.contents[0].text)

                # Read another dynamic resource
                print("\n" + "=" * 50)
                print("READING: note://notes/note2")
                print("=" * 50)
                note2 = await session.read_resource("note://notes/note2")
                print(note2.contents[0].text)

                print("\n" + "=" * 50)
                print("ALL TESTS COMPLETED SUCCESSFULLY")
                print("=" * 50 + "\n")

    except asyncio.CancelledError:
        print("\n⚠️  Operation cancelled")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_resources())
