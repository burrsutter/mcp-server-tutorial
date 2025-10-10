# Example 4: MCP Server with Resources

This example demonstrates MCP resources - both static and dynamic data sources that clients can access.

## What This Example Demonstrates

- Static resources with fixed URIs
- Dynamic resources using URI templates
- Resource metadata (name, mimeType, description)
- Reading resource content by URI
- Different content types (text/plain, application/json)

## Files

- `server.py` - MCP server with resources
- `requirements.txt` - Python dependencies

## Resources vs Tools

**Resources** are read-only data sources:
- Represent data that can be retrieved
- Use URIs for identification
- Good for: configuration, documentation, data exports

**Tools** are executable functions:
- Perform actions or computations
- Can modify state
- Good for: operations, transformations, API calls

## Available Resources

### Static Resources
1. **note://static/welcome**
   - Plain text welcome message
   - Always returns the same content

2. **note://static/info**
   - JSON server information
   - Includes timestamp (changes each read)

### Dynamic Resources (Templates)
1. **note://notes/{id}**
   - Access notes by ID
   - Available IDs: `note1`, `note2`
   - Example: `note://notes/note1`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Testing with a Client

Create a test client to access resources:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_resources():
    server_params = StdioServerParameters(
        command="python",
        args=["../04-server-with-resources/server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List all resources
            resources = await session.list_resources()
            print("Available resources:", resources)
            
            # Read a static resource
            content = await session.read_resource("note://static/welcome")
            print(content)
            
            # Read a dynamic resource
            note = await session.read_resource("note://notes/note1")
            print(note)
```

## Key Concepts

### Resource Definition
```python
Resource(
    uri="note://static/welcome",      # Unique identifier
    name="Welcome Note",                # Human-readable name
    mimeType="text/plain",              # Content type
    description="A static welcome message"  # What it contains
)
```

### URI Schemes
Use custom URI schemes to organize resources:
- `note://static/...` - Static resources
- `note://notes/...` - Dynamic note resources
- `config://...` - Configuration resources
- `data://...` - Data exports

### Resource Templates
Templates allow dynamic resource access:
```python
Resource(
    uri="note://notes/{id}",  # {id} is a placeholder
    name="Note by ID",
    description="Access notes: note1, note2"
)
```

Clients can access:
- `note://notes/note1`
- `note://notes/note2`
- etc.

### Reading Resources
```python
@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri.startswith("note://notes/"):
        note_id = uri.split("/")[-1]
        return NOTES[note_id]
```

## When to Use Resources

Use resources when:
- Providing read-only data
- Exposing configuration or documentation
- Sharing structured data (JSON, XML, etc.)
- Creating data catalogs

Use tools when:
- Performing actions or operations
- Modifying state
- Making API calls
- Running computations

## Next Steps

- See Example 5 for a server that combines both tools and resources
- See Example 6 for an advanced client that uses both features
