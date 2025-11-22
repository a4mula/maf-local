"""
FastAPI endpoint to expose the Liaison Agent for UI communication.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

app = FastAPI(title="MAF Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In production, specify UI URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
from src.api.routes import projects, sessions
app.include_router(projects.router)
app.include_router(sessions.router)

# Global reference to the agent hierarchy (set during startup)
agent_hierarchy = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None

def set_agent_hierarchy(hierarchy):
    """Called from main.py to inject the agent hierarchy."""
    global agent_hierarchy
    agent_hierarchy = hierarchy

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "maf-agent-api"}

# Global active context for visualization (Project/Session)
active_context = {
    "project_id": 0,
    "project_name": "DevStudio (Self)",
    "session_id": None,
    "session_name": None
}

class ContextUpdate(BaseModel):
    project_id: int
    project_name: str
    session_id: Optional[int] = None
    session_name: Optional[str] = None

@app.post("/api/context")
async def update_context(ctx: ContextUpdate):
    """Update the global active context for visualization."""
    global active_context
    active_context = ctx.dict()
    return {"status": "updated", "context": active_context}

@app.get("/api/agents/status")
async def get_agent_status():
    """
    Returns current status of all agents in the hierarchy.
    """
    if agent_hierarchy is None:
        # Return mock data if hierarchy not yet initialized (e.g. during startup)
        return {
            "nodes": [],
            "connections": [],
            "activeContext": active_context,
            "lastUpdated": datetime.utcnow().isoformat()
        }

    nodes = []
    connections = []
    
    # Helper to add node
    def add_node(id, name, tier, status="idle", task=None):
        nodes.append({
            "id": id,
            "name": name,
            "tier": tier,
            "status": status,
            "currentTask": task,
            "metrics": {
                "tokensUsed": 0, # Placeholder
                "timeInState": 0, # Placeholder
                "messagesProcessed": 0 # Placeholder
            }
        })

    # 1. Liaison
    liaison = agent_hierarchy.get("liaison")
    add_node("liaison", "Liaison", "liaison", "active" if liaison else "error", "Listening for user input")

    # 2. Project Lead
    pl = agent_hierarchy.get("project_lead")
    add_node("pl", "Project Lead", "project-lead", "idle", "Waiting for tasks")
    
    if liaison and pl:
        connections.append({"from": "liaison", "to": "pl", "active": False})

    # 3. Domain Leads
    dls = agent_hierarchy.get("domain_leads", {})
    for key, dl in dls.items():
        node_id = f"dl-{key}"
        add_node(node_id, f"{key.capitalize()} DL", "domain-lead", "idle")
        if pl:
            connections.append({"from": "pl", "to": node_id, "active": False})
            
    # 4. Executors
    execs = agent_hierarchy.get("executors", {})
    for key, exc in execs.items():
        node_id = f"exec-{key}"
        add_node(node_id, f"{key.capitalize()}", "executor", "idle")
        # Connect executors to Dev DL for now as default, or based on logic
        # For visualization, we might want to show them connected to relevant DLs
        # Assuming 'coder' and 'tester' go to 'dev' and 'qa' respectively for demo
        parent_dl = "dl-dev" if key == "coder" else "dl-qa" if key == "tester" else "dl-docs"
        if parent_dl in [f"dl-{k}" for k in dls.keys()]:
             connections.append({"from": parent_dl, "to": node_id, "active": False})

    return {
        "nodes": nodes,
        "connections": connections,
        "activeContext": active_context,
        "lastUpdated": datetime.utcnow().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a user message through the Liaison Agent.
    """
    if agent_hierarchy is None or "liaison" not in agent_hierarchy:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    liaison_agent = agent_hierarchy["liaison"]
    
    try:
        # TODO: Inject session_id into agent context here if needed
        response = await liaison_agent.handle_user_message(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Hierarchical MAF Studio API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "status": "/api/agents/status",
            "context": "/api/context (POST)"
        }
    }
