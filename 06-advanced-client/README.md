# Example 6: Advanced MCP Client

This example demonstrates a comprehensive MCP client with advanced features including error handling, capability exploration, and complete workflow demonstrations.

## What This Example Demonstrates

- Complete client workflow
- Server capability discovery
- CRUD operations demonstration
- Search functionality
- Resource access patterns
- Comprehensive error handling
- Structured output formatting
- Best practices for MCP clients

## Files

- `client.py` - Advanced MCP client with full feature set
- `requirements.txt` - Python dependencies

## Prerequisites

This client requires Example 5's server to be available:
- Ensure `../05-complete-server/server.py` exists
- The server should be functional and up-to-date

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Client

```bash
python client.py
```

The client will automatically:
1. Connect to the notes server
2. Explore server capabilities
3. Demonstrate CRUD operations
4. Show search functionality
5. Access resources
6. Test error handling

## Features

### 1. Server Capability Discovery
Lists all available:
- Tools and their descriptions
- Static resources
- Resource templates

### 2. CRUD Operations
Complete workflow:
- **Create**: Add a new note with tags
- **Read**: Access note via resource URI
- **Update**: Modify note content and tags
- **Delete**: Remove note from system

### 3. Search Demonstrations
Multiple search scenarios:
- Keyword search in content
- Tag-based search
- Handling no results

### 4. Resource Access
Different resource types:
- Plain text summary
- JSON data export
- Dynamic resource templates

### 5. Error Handling
Graceful handling of:
- Non-existent resources
- Invalid tool calls
- Missing data
- Server errors

## Output Example

```
🚀 Advanced MCP Client Demo
Connecting to the notes server...

✅ Connected successfully!

============================================================
  SERVER CAPABILITIES
============================================================

📋 Available Tools:
  • create_note: Create a new note
  • update_note: Update an existing note
  • delete_note: Delete a note
  • search_notes: Search notes by keyword or tag

Total tools: 4

📦 Available Resources:
  • notes://list
    Name: All Notes
    Type: application/json
  • notes://summary
    Name: Notes Summary
    Type: text/plain
...
```

## Key Concepts

### Async Context Managers
```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Client operations here
```
Ensures proper connection handling and cleanup.

### Capability Discovery
```python
tools = await session.list_tools()
resources = await session.list_resources()
templates = await session.list_resource_templates()
```
Always explore what's available before using it.

### Error Handling Pattern
```python
try:
    result = await session.call_tool(name, arguments)
    print(f"✅ {result.content[0].text}")
except Exception as e:
    print(f"❌ Error: {e}")
```
Always wrap MCP operations in try-except blocks.

### Resource URI Construction
```python
# Static resource
content = await session.read_resource("notes://list")

# Dynamic resource with template
note_id = "2"
content = await session.read_resource(f"notes://note/{note_id}")
```

## Best Practices Demonstrated

1. **Initialize First**: Always call `session.initialize()` before operations
2. **Explore Capabilities**: List available tools/resources before using
3. **Handle Errors**: Wrap operations in try-except blocks
4. **Close Gracefully**: Use context managers for automatic cleanup
5. **User Feedback**: Provide clear status messages
6. **Type Safety**: Parse JSON responses properly
7. **Modular Design**: Separate concerns into functions

## Customization

Modify the demonstrations:
```python
# Add your own test cases
async def demonstrate_custom_feature(session):
    await print_separator("CUSTOM FEATURE")
    
    # Your code here
    result = await session.call_tool(
        "your_tool",
        arguments={"key": "value"}
    )
    print(result.content[0].text)

# Call in main()
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await demonstrate_custom_feature(session)
```

## Troubleshooting

**Connection Errors**
- Verify server path in `StdioServerParameters`
- Check that Python is in your PATH
- Ensure server has no syntax errors

**Import Errors**
- Install dependencies: `pip install -r requirements.txt`
- Use virtual environment
- Check Python version (3.9+)

**Runtime Errors**
- Review server logs for issues
- Verify tool/resource names match server
- Check argument formats match schemas

## Learning Path

Use this client to:
1. Understand MCP client architecture
2. Learn async patterns in Python
3. Practice error handling
4. Explore server capabilities
5. Build your own MCP applications

## Next Steps

- See Example 7 for external API integration
- See Example 8 for FastAPI + MCP combination
- See Example 9 for Kubernetes deployment
- Build your own client with custom features
