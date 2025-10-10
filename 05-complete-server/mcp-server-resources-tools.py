#!/usr/bin/env python3
"""
Example 5: Complete MCP Server
Combines tools and resources in a realistic note-taking system.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, TextContent


# Create the server instance
server = Server("notes-server")

# In-memory note storage
notes: Dict[str, dict] = {
    "1": {
        "title": "Welcome",
        "content": "Welcome to the notes system!",
        "created": "2024-01-15T10:00:00",
        "updated": "2024-01-15T10:00:00",
        "tags": ["welcome", "info"]
    }
}
note_counter = 2  # Next ID to use


# ============= TOOLS =============

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="create_note",
            description="Create a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Note title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Note content"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for the note"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="update_note",
            description="Update an existing note",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Note ID"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags (optional)"
                    }
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="delete_note",
            description="Delete a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Note ID to delete"
                    }
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="search_notes",
            description="Search notes by keyword or tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "search_tags": {
                        "type": "boolean",
                        "description": "Search in tags as well",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""
    global note_counter
    
    if name == "create_note":
        title = arguments["title"]
        content = arguments["content"]
        tags = arguments.get("tags", [])
        
        note_id = str(note_counter)
        note_counter += 1
        
        now = datetime.now().isoformat()
        notes[note_id] = {
            "title": title,
            "content": content,
            "created": now,
            "updated": now,
            "tags": tags
        }
        
        return [TextContent(
            type="text",
            text=f"Created note with ID: {note_id}\nTitle: {title}\nTags: {', '.join(tags) if tags else 'none'}"
        )]
    
    elif name == "update_note":
        note_id = arguments["id"]
        
        if note_id not in notes:
            return [TextContent(
                type="text",
                text=f"Error: Note {note_id} not found"
            )]
        
        note = notes[note_id]
        updated = False
        
        if "title" in arguments:
            note["title"] = arguments["title"]
            updated = True
        if "content" in arguments:
            note["content"] = arguments["content"]
            updated = True
        if "tags" in arguments:
            note["tags"] = arguments["tags"]
            updated = True
        
        if updated:
            note["updated"] = datetime.now().isoformat()
        
        return [TextContent(
            type="text",
            text=f"Updated note {note_id}\nTitle: {note['title']}\nLast updated: {note['updated']}"
        )]
    
    elif name == "delete_note":
        note_id = arguments["id"]
        
        if note_id not in notes:
            return [TextContent(
                type="text",
                text=f"Error: Note {note_id} not found"
            )]
        
        deleted_note = notes.pop(note_id)
        return [TextContent(
            type="text",
            text=f"Deleted note {note_id}: {deleted_note['title']}"
        )]
    
    elif name == "search_notes":
        query = arguments["query"].lower()
        search_tags = arguments.get("search_tags", True)
        
        results = []
        for note_id, note in notes.items():
            # Search in title and content
            if query in note["title"].lower() or query in note["content"].lower():
                results.append(f"ID: {note_id} - {note['title']}")
            # Search in tags if enabled
            elif search_tags and any(query in tag.lower() for tag in note["tags"]):
                results.append(f"ID: {note_id} - {note['title']} [tag match]")
        
        if results:
            return [TextContent(
                type="text",
                text=f"Found {len(results)} note(s):\n" + "\n".join(results)
            )]
        else:
            return [TextContent(
                type="text",
                text=f"No notes found matching: {query}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# ============= RESOURCES =============

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List all available static resources."""
    return [
        Resource(
            uri="notes://list",
            name="All Notes",
            mimeType="application/json",
            description="List of all notes with metadata"
        ),
        Resource(
            uri="notes://summary",
            name="Notes Summary",
            mimeType="text/plain",
            description="Summary of all notes"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource by URI."""
    uri = str(uri)  # Convert AnyUrl to string

    if uri == "notes://list":
        # Return all notes as JSON
        return json.dumps(notes, indent=2)
    
    elif uri == "notes://summary":
        # Return a text summary
        if not notes:
            return "No notes available."
        
        summary = f"Total Notes: {len(notes)}\n\n"
        for note_id, note in notes.items():
            summary += f"ID: {note_id}\n"
            summary += f"Title: {note['title']}\n"
            summary += f"Created: {note['created']}\n"
            summary += f"Tags: {', '.join(note['tags']) if note['tags'] else 'none'}\n"
            summary += "-" * 40 + "\n"
        
        return summary
    
    # Dynamic resource: individual notes
    elif uri.startswith("notes://note/"):
        note_id = uri.split("/")[-1]
        
        if note_id in notes:
            note = notes[note_id]
            return json.dumps(note, indent=2)
        else:
            raise ValueError(f"Note not found: {note_id}")
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@server.list_resource_templates()
async def list_resource_templates() -> list[Resource]:
    """List resource templates for dynamic resource access."""
    return [
        Resource(
            uri="notes://note/{id}",
            name="Note by ID",
            mimeType="application/json",
            description=f"Access a specific note. Available IDs: {', '.join(notes.keys())}"
        )
    ]


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
