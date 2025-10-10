# Example 5: Complete MCP Server

This example demonstrates a realistic MCP server that combines both tools and resources in a functional note-taking system.

## What This Example Demonstrates

- Combining tools and resources in one server
- CRUD operations (Create, Read, Update, Delete)
- In-memory state management
- Search functionality
- Multiple resources with different content types
- Dynamic resource templates
- Practical application structure

## Files

- `server.py` - Complete MCP server with notes system
- `requirements.txt` - Python dependencies

## Features

### Tools (Actions)
1. **create_note** - Create a new note with title, content, and tags
2. **update_note** - Update an existing note's fields
3. **delete_note** - Remove a note by ID
4. **search_notes** - Search notes by keywords or tags

### Resources (Data Access)
1. **notes://list** - JSON export of all notes
2. **notes://summary** - Text summary of all notes
3. **notes://note/{id}** - Access individual notes by ID

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage Example

Here's a complete workflow using this server:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def demo():
    server_params = StdioServerParameters(
        command="python",
        args=["../05-complete-server/server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create a note
            result = await session.call_tool(
                "create_note",
                arguments={
                    "title": "Shopping List",
                    "content": "Buy milk, eggs, bread",
                    "tags": ["shopping", "todo"]
                }
            )
            print(result.content[0].text)
            
            # Search for notes
            result = await session.call_tool(
                "search_notes",
                arguments={"query": "shopping"}
            )
            print(result.content[0].text)
            
            # Read notes summary resource
            summary = await session.read_resource("notes://summary")
            print(summary)
            
            # Update a note
            result = await session.call_tool(
                "update_note",
                arguments={
                    "id": "2",
                    "content": "Buy milk, eggs, bread, cheese"
                }
            )
            print(result.content[0].text)
            
            # Access specific note via resource
            note = await session.read_resource("notes://note/2")
            print(note)
            
            # Delete a note
            result = await session.call_tool(
                "delete_note",
                arguments={"id": "2"}
            )
            print(result.content[0].text)
```

## Architecture

### State Management
```python
notes: Dict[str, dict] = {
    "1": {
        "title": "Welcome",
        "content": "...",
        "created": "2024-01-15T10:00:00",
        "updated": "2024-01-15T10:00:00",
        "tags": ["welcome"]
    }
}
```

Notes are stored in memory with:
- Unique ID (string)
- Title and content
- Created/updated timestamps
- Optional tags array

### Tool vs Resource Design

**Tools** modify state:
- `create_note` - Adds new note
- `update_note` - Modifies existing note
- `delete_note` - Removes note
- `search_notes` - Queries notes (read-only but dynamic)

**Resources** expose data:
- `notes://list` - All notes as JSON
- `notes://summary` - Formatted summary
- `notes://note/{id}` - Individual note access

## Key Concepts

### Combining Tools and Resources

Tools and resources work together:
1. Use **tools** to modify data
2. Use **resources** to view data
3. Resources automatically reflect tool changes

### State Persistence

This example uses in-memory storage. For production:
- Add database integration
- Implement file-based persistence
- Add transaction support

### Error Handling

The server includes basic error handling:
```python
if note_id not in notes:
    return [TextContent(
        type="text",
        text=f"Error: Note {note_id} not found"
    )]
```

### Optional Parameters

Tools support optional parameters:
```python
Tool(
    name="update_note",
    inputSchema={
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},  # Optional
            "content": {"type": "string"}  # Optional
        },
        "required": ["id"]  # Only ID required
    }
)
```

## Extension Ideas

Enhance this server by adding:
- Note categories/folders
- Full-text search
- Note sharing/permissions
- Export to different formats
- Trash/archive functionality
- Note templates

## Output

```
Created note with ID: 2
Title: Shopping List
Tags: shopping, todo
Found 1 note(s):
ID: 2 - Shopping List
meta=None contents=[TextResourceContents(uri=AnyUrl('notes://summary'), mimeType='text/plain', meta=None, text='Total Notes: 2\n\nID: 1\nTitle: Welcome\nCreated: 2024-01-15T10:00:00\nTags: welcome, info\n----------------------------------------\nID: 2\nTitle: Shopping List\nCreated: 2025-10-09T18:22:20.373431\nTags: shopping, todo\n----------------------------------------\n')]
Updated note 2
Title: Shopping List
Last updated: 2025-10-09T18:22:20.377157
meta=None contents=[TextResourceContents(uri=AnyUrl('notes://note/2'), mimeType='text/plain', meta=None, text='{\n  "title": "Shopping List",\n  "content": "Buy milk, eggs, bread, cheese",\n  "created": "2025-10-09T18:22:20.373431",\n  "updated": "2025-10-09T18:22:20.377157",\n  "tags": [\n    "shopping",\n    "todo"\n  ]\n}')]
Deleted note 2: Shopping List
```