from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Math Operations Server")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    result = a + b
    print(f"Add: {a} + {b} = {result}")
    return result

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first number.

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
    """
    result = a - b
    print(f"Subtract: {a} - {b} = {result}")
    return result

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number
    """
    result = a * b
    print(f"Multiply: {a} * {b} = {result}")
    return result

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide the first number by the second number.

    Args:
        a: Dividend (number to be divided)
        b: Divisor (number to divide by)
    """
    if b == 0:
        print(f"Divide by zero error: {a} / {b}")
        raise ValueError("Cannot divide by zero")
    
    result = a / b
    print(f"Divide: {a} / {b} = {result}")
    return result

if __name__ == "__main__":
    # Use HTTP transport
    mcp.run(transport="http", port=9005)
