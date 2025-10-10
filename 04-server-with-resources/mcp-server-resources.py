#!/usr/bin/env python3
"""
Example 4: MCP Server with Resources
Demonstrates MCP resources - static and dynamic data sources.
"""

import asyncio
import json
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, ResourceTemplate, TextContent


# Create the server instance
server = Server("resource-server")


# Sample data
NOTES = {
    "note1": {
        "title": "Meeting Notes",
        "content": "Discussed project timeline and milestones",
        "created": "2024-01-15"
    },
    "note2": {
        "title": "Ideas",
        "content": "New features to implement in Q2",
        "created": "2024-01-16"
    }
}


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List all available static resources."""
    return [
        Resource(
            uri="note://static/welcome",
            name="Welcome Note",
            mimeType="text/plain",
            description="A static welcome message"
        ),
        Resource(
            uri="note://static/info",
            name="Server Info",
            mimeType="application/json",
            description="Information about this MCP server"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource by URI."""
    try:
        # Convert AnyUrl to string if needed
        uri_str = str(uri)

        # Validate URI scheme
        if not uri_str.startswith("note://"):
            raise ValueError(f"Invalid URI scheme. Expected 'note://', got: {uri_str}")

        # Static resources
        if uri_str == "note://static/welcome":
            return "Welcome to the MCP Resource Server!\n\nThis server demonstrates static and dynamic resources."

        elif uri_str == "note://static/info":
            info = {
                "name": "Resource Demo Server",
                "version": "1.0.0",
                "capabilities": ["static_resources", "resource_templates"],
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(info, indent=2)

        # Dynamic resources (template-based)
        elif uri_str.startswith("note://notes/"):
            # Extract note ID from URI: note://notes/{id}
            note_id = uri_str.split("/")[-1]

            if not note_id:
                raise ValueError("Note ID cannot be empty")

            if note_id in NOTES:
                note = NOTES[note_id]
                return f"Title: {note['title']}\nCreated: {note['created']}\n\n{note['content']}"
            else:
                available_ids = ", ".join(NOTES.keys())
                raise ValueError(f"Note not found: '{note_id}'. Available notes: {available_ids}")

        else:
            raise ValueError(f"Unknown resource URI: {uri_str}")

    except Exception as e:
        # Log the error for debugging
        import sys
        print(f"Error reading resource {uri_str}: {e}", file=sys.stderr)
        raise


@server.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """List resource templates for dynamic resource access."""
    return [
        ResourceTemplate(
            uriTemplate="note://notes/{id}",
            name="Note by ID",
            mimeType="text/plain",
            description=f"Access a specific note. Available IDs: {', '.join(NOTES.keys())}"
        )
    ]


async def main():
    """Run the server using stdio transport."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except asyncio.CancelledError:
        # Handle cancellation gracefully
        import sys
        print("Server cancelled", file=sys.stderr)
        raise
    except Exception as e:
        import sys
        print(f"Server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(main())
