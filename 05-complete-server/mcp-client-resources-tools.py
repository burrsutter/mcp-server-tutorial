import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def demo():
    server_params = StdioServerParameters(
        command="python",
        args=["./05-complete-server/mcp-server-resources-tools.py"],
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

if __name__ == "__main__":
    asyncio.run(demo())
