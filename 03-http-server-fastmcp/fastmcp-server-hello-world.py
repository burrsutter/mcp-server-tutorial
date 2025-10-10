from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Hello World Server")

@mcp.tool()
def say_hello(name: str = "World") -> str:
    """Say hello to someone.

    Args:
        name: The name to greet (defaults to "World")
    """
    print(f"Console log: Input parameter 'name' = {name}")
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="http", port=9000)
