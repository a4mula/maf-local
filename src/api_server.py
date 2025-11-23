"""
Standalone entry point for the FastAPI Agent API server.
This initializes the agent hierarchy and starts the server.
"""
import asyncio
from src.services.agent_factory import AgentFactory
from src.api.agent_api import app, set_agent_hierarchy
from src.config.settings import settings
import uvicorn

# Ensure tools are registered
import src.tools.code_tools

def startup():
    """Initialize agent hierarchy before starting the server."""
    print("[System] Initializing Agent Hierarchy...")
    hierarchy = AgentFactory.create_hierarchy()
    
    # Inject hierarchy into the API
    set_agent_hierarchy(hierarchy)
    
    print(f"[System] Agent Hierarchy initialized.")
    print(f"[System] Active Agents: Liaison, ProjectLead")
    print(f"[System] Starting API server on http://0.0.0.0:8002")

# Register startup event
@app.on_event("startup")
async def on_startup():
    """Run startup initialization."""
    startup()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
