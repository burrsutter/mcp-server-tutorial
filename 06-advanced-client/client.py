#!/usr/bin/env python3
"""
Example 6: Advanced MCP Client
Demonstrates comprehensive client features including error handling,
listing capabilities, and using both tools and resources.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def print_separator(title: str):
    """Print a formatted section separator."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


async def explore_server_capabilities(session: ClientSession):
    """Explore and display all server capabilities."""
    await print_separator("SERVER CAPABILITIES")
    
    # List tools
    print("📋 Available Tools:")
    tools_response = await session.list_tools()
    for tool in tools_response.tools:
        print(f"  • {tool.name}: {tool.description}")
    
    print(f"\nTotal tools: {len(tools_response.tools)}\n")
    
    # List resources
    print("📦 Available Resources:")
    resources_response = await session.list_resources()
    for resource in resources_response.resources:
        print(f"  • {resource.uri}")
        print(f"    Name: {resource.name}")
        print(f"    Type: {resource.mimeType}")
    
    print(f"\nTotal resources: {len(resources_response.resources)}\n")
    
    # List resource templates
    print("🔧 Resource Templates:")
    templates_response = await session.list_resource_templates()
    for template in templates_response.resourceTemplates:
        print(f"  • {template.uri}")
        print(f"    Name: {template.name}")
        print(f"    Description: {template.description}")


async def demonstrate_crud_operations(session: ClientSession):
    """Demonstrate Create, Read, Update, Delete operations."""
    await print_separator("CRUD OPERATIONS")
    
    # CREATE
    print("➕ Creating a new note...")
    try:
        result = await session.call_tool(
            "create_note",
            arguments={
                "title": "Python Best Practices",
                "content": "1. Use virtual environments\n2. Follow PEP 8\n3. Write tests",
                "tags": ["python", "programming", "tips"]
            }
        )
        print(f"✅ {result.content[0].text}\n")
        created_note_id = "2"  # We know this will be ID 2
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return
    
    # READ via resource
    print("📖 Reading the note via resource...")
    try:
        note_content = await session.read_resource(f"notes://note/{created_note_id}")
        note_data = json.loads(note_content)
        print(f"✅ Retrieved note: {note_data['title']}")
        print(f"   Tags: {', '.join(note_data['tags'])}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # UPDATE
    print("✏️  Updating the note...")
    try:
        result = await session.call_tool(
            "update_note",
            arguments={
                "id": created_note_id,
                "content": "1. Use virtual environments\n2. Follow PEP 8\n3. Write tests\n4. Use type hints",
                "tags": ["python", "programming", "tips", "updated"]
            }
        )
        print(f"✅ {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # DELETE
    print("🗑️  Deleting the note...")
    try:
        result = await session.call_tool(
            "delete_note",
            arguments={"id": created_note_id}
        )
        print(f"✅ {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


async def demonstrate_search(session: ClientSession):
    """Demonstrate search functionality."""
    await print_separator("SEARCH OPERATIONS")
    
    # Create test notes
    print("📝 Creating test notes for search...")
    test_notes = [
        {"title": "MCP Protocol", "content": "Model Context Protocol documentation", "tags": ["mcp", "docs"]},
        {"title": "Python Tutorial", "content": "Learn Python programming", "tags": ["python", "tutorial"]},
        {"title": "MCP Examples", "content": "Code examples for MCP", "tags": ["mcp", "examples"]},
    ]
    
    for note in test_notes:
        try:
            await session.call_tool("create_note", arguments=note)
        except Exception as e:
            print(f"⚠️  Warning: {e}")
    
    print("✅ Test notes created\n")
    
    # Search by keyword
    print("🔍 Searching for 'MCP'...")
    try:
        result = await session.call_tool(
            "search_notes",
            arguments={"query": "MCP"}
        )
        print(f"✅ {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Search by tag
    print("🔍 Searching for 'python' (including tags)...")
    try:
        result = await session.call_tool(
            "search_notes",
            arguments={"query": "python", "search_tags": True}
        )
        print(f"✅ {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Search with no results
    print("🔍 Searching for 'nonexistent'...")
    try:
        result = await session.call_tool(
            "search_notes",
            arguments={"query": "nonexistent"}
        )
        print(f"✅ {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


async def demonstrate_resources(session: ClientSession):
    """Demonstrate resource access."""
    await print_separator("RESOURCE ACCESS")
    
    # Read summary
    print("📊 Reading notes summary...")
    try:
        summary = await session.read_resource("notes://summary")
        print(summary)
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Read full list as JSON
    print("📋 Reading all notes as JSON...")
    try:
        notes_json = await session.read_resource("notes://list")
        notes = json.loads(notes_json)
        print(f"✅ Retrieved {len(notes)} note(s)")
        print(f"   Note IDs: {', '.join(notes.keys())}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


async def demonstrate_error_handling(session: ClientSession):
    """Demonstrate error handling."""
    await print_separator("ERROR HANDLING")
    
    # Try to update non-existent note
    print("⚠️  Attempting to update non-existent note...")
    try:
        result = await session.call_tool(
            "update_note",
            arguments={"id": "999", "title": "This won't work"}
        )
        print(f"Response: {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Exception caught: {e}\n")
    
    # Try to delete non-existent note
    print("⚠️  Attempting to delete non-existent note...")
    try:
        result = await session.call_tool(
            "delete_note",
            arguments={"id": "999"}
        )
        print(f"Response: {result.content[0].text}\n")
    except Exception as e:
        print(f"❌ Exception caught: {e}\n")
    
    # Try to access non-existent resource
    print("⚠️  Attempting to access non-existent resource...")
    try:
        content = await session.read_resource("notes://note/999")
        print(f"Content: {content}\n")
    except Exception as e:
        print(f"❌ Exception caught: {e}\n")
    
    # Try to call non-existent tool
    print("⚠️  Attempting to call non-existent tool...")
    try:
        result = await session.call_tool(
            "nonexistent_tool",
            arguments={}
        )
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"❌ Exception caught: {e}\n")


async def main():
    """Main client function demonstrating advanced MCP features."""
    
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["../05-complete-server/server.py"],
    )
    
    print("🚀 Advanced MCP Client Demo")
    print("Connecting to the notes server...\n")
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                print("✅ Connected successfully!\n")
                
                # Run demonstrations
                await explore_server_capabilities(session)
                await demonstrate_crud_operations(session)
                await demonstrate_search(session)
                await demonstrate_resources(session)
                await demonstrate_error_handling(session)
                
                await print_separator("DEMO COMPLETE")
                print("All operations completed successfully!")
                print("Check the examples above to see how to:")
                print("  • Connect to MCP servers")
                print("  • List and use tools")
                print("  • Access resources")
                print("  • Handle errors gracefully")
                print("  • Build robust MCP clients\n")
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Make sure the server is accessible and properly configured.")


if __name__ == "__main__":
    asyncio.run(main())
