"""
FastAPI wrapper for LangGraph agent that connects to MCP server
Provides REST API endpoint for math operations via the agent
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configuration from environment variables
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9005/mcp")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Global variables to store the agent and tools
agent = None
client = None


class AddRequest(BaseModel):
    """Request model for addition operation"""
    a: float
    b: float


class AddResponse(BaseModel):
    """Response model for addition operation"""
    result: float
    query: str
    agent_response: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MCP client and agent on startup"""
    global agent, client

    print("Initializing MCP client and LangGraph agent...")
    print(f"Connecting to MCP server at: {MCP_SERVER_URL}")

    # Create MCP client with http connection to our FastMCP server
    client = MultiServerMCPClient(
        connections={
            "math_server": {
                "url": MCP_SERVER_URL,
                "transport": "streamable_http",  # Use http transport for FastMCP
            }
        }
    )

    # Load tools from the MCP server
    tools = await client.get_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # Create a LangGraph agent that can use MCP tools
    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = create_react_agent(llm, tools=tools)

    print("Agent initialized successfully!")

    yield

    # Cleanup on shutdown
    print("Shutting down...")


app = FastAPI(
    title="LangGraph Agent API",
    description="REST API wrapper for LangGraph agent with MCP tools",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/add", response_model=AddResponse)
async def add_numbers(request: AddRequest) -> AddResponse:
    """
    Add two numbers using the LangGraph agent with MCP tools

    Args:
        request: AddRequest containing two numbers (a and b)

    Returns:
        AddResponse with the result and agent details
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Construct the query for the agent
        query = f"Use the add tool to add {request.a} and {request.b}"

        # Run the agent query
        result = await agent.ainvoke({"messages": [("user", query)]})

        # Extract the numeric result as a float from the tool call result
        answer = None
        for message in result["messages"]:
            if hasattr(message, 'type') and message.type == 'tool':
                # This is a tool result message containing the actual float return value
                answer = float(message.content)
                break

        if answer is None:
            # Fallback: try to extract from final message
            final_message = result["messages"][-1]
            try:
                answer = float(final_message.content)
            except (ValueError, AttributeError):
                raise HTTPException(
                    status_code=500,
                    detail="Could not extract numeric result from agent response"
                )

        # Get the final agent response content
        final_message = result["messages"][-1]
        agent_response = final_message.content if hasattr(final_message, 'content') else str(final_message)

        return AddResponse(
            result=answer,
            query=query,
            agent_response=agent_response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint with MCP server connectivity check"""
    health_status = {
        "status": "unhealthy",
        "agent_initialized": agent is not None,
        "mcp_server_connected": False,
        "available_tools": []
    }

    if agent is None or client is None:
        return health_status

    try:
        # Try to get tools from MCP server to verify connectivity
        tools = await client.get_tools()
        health_status["mcp_server_connected"] = True
        health_status["available_tools"] = [tool.name for tool in tools]
        health_status["status"] = "healthy"
    except Exception as e:
        health_status["mcp_server_error"] = str(e)

    return health_status


if __name__ == "__main__":
    import uvicorn
    print(f"Starting FastAPI server on port {API_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
