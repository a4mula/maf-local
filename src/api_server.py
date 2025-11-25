"""
Standalone entry point for the FastAPI Agent API server.
This initializes the agent hierarchy and starts the server.
"""
import asyncio
from src.services.agent_factory import AgentFactory
from src.api.agent_api import app, set_agent_hierarchy
from src.config.settings import settings
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure tools are registered
# import src.tools.code_tools  <-- REMOVED: Imported via src.tools re-export

def startup():
    """Initialize agent hierarchy before starting the server."""
    logger.info("Startup complete. Server ready.")
    logger.info(f"Environment: {os.getenv('MAF_ENV', 'development')}")
    logger.info("Initializing agent hierarchy...")
    hierarchy = AgentFactory.create_hierarchy()
    
    # Inject hierarchy into the API
    set_agent_hierarchy(hierarchy)
    
    logger.info(f"Active Agents: Liaison, ProjectLead")
    logger.info(f"Starting API server on http://0.0.0.0:8002")

# Register startup event
@app.on_event("startup")
async def on_startup():
    """Run startup initialization."""
    startup()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
