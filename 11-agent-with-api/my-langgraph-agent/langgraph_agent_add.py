"""
Simple LangGraph agent that connects to MCP server via HTTP
Uses langchain_mcp_adapters for seamless integration.
"""
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    # 1 Create MCP client with http connection to our FastMCP server
    print("Connecting to MCP server at http://localhost:9005/mcp...")

    client = MultiServerMCPClient(
        connections={
            "math_server": {
                "url": "http://localhost:9005/mcp",
                "transport": "streamable_http",  # Use http transport for FastMCP
            }
        }
    )

    # 2 Load tools from the MCP server
    print("Loading tools from MCP server...")
    tools = await client.get_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # 3 Create a LangGraph agent that can use MCP tools
    print("Creating LangGraph agent...")
    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = create_react_agent(llm, tools=tools)

    # 4 Run a simple query
    print("\n--- Running agent query ---")
    result = await agent.ainvoke({"messages": [("user", "Use the add tool to add 2 and 3")]})

    # 5 Extract the numeric result as a float from the tool call result
    answer = None
    for message in result["messages"]:
        if hasattr(message, 'type') and message.type == 'tool':
            # This is a tool result message containing the actual float return value
            answer = float(message.content)
            break

    if answer is None:
        # Fallback: try to extract from final message
        final_message = result["messages"][-1]
        answer = float(final_message.content)


    print("\n--- Agent Answer ---")
    print(f"Result: {answer} (type: {type(answer).__name__})")


    print("\n--- Agent Response content---")
    final_message = result["messages"][-1]
    print(final_message.content)

    print("\n--- Full Agent Response ---")
    print(result)
    


if __name__ == "__main__":
    asyncio.run(main())