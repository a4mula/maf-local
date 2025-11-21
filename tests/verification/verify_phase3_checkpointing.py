import asyncio
import uuid
from agent_framework import ChatMessage
from src.persistence.checkpoint_storage import PostgreSQLCheckpointStorage
from src.workflows.maf_workflow import create_development_workflow
from src.services.agent_factory import AgentFactory
from src.config.settings import settings

async def verify_checkpointing():
    print("--- Verifying Phase 3: Workflow Checkpointing ---")
    
    # 1. Initialize Storage
    print("[1] Initializing Checkpoint Storage...")
    storage = PostgreSQLCheckpointStorage(settings.DATABASE_URL)
    
    # 2. Create Agents
    print("[2] Creating Agents...")
    hierarchy = AgentFactory.create_hierarchy()
    pl = hierarchy["project_lead"]
    dl = hierarchy["domain_leads"]["dev"]
    
    # 3. Create Workflow
    print("[3] Creating Workflow...")
    workflow = create_development_workflow(pl, dl, storage)
    print(f"   Workflow ID: {workflow.id}")
    
    # 4. Run Workflow (First Pass)
    print("[4] Running Workflow...")
    task = "Build a login form"
    
    # We run the workflow with an initial message
    # The run() method returns a WorkflowRunResult
    result = await workflow.run(message=ChatMessage(role="user", text=task))
    
    print(f"   Run complete. Status: {result.get_final_state()}")
    
    # 5. Verify Checkpoint Persistence
    print("[5] Verifying Checkpoint Persistence...")
    # List checkpoints for this workflow
    checkpoints = await storage.list_checkpoints(workflow.id)
    
    if len(checkpoints) > 0:
        print(f"✅ Found {len(checkpoints)} checkpoints.")
        latest = checkpoints[0]
        print(f"   Latest Checkpoint ID: {latest.checkpoint_id}")
        print(f"   Iteration: {latest.iteration_count}")
    else:
        print("❌ No checkpoints found!")
        exit(1)
        
    print("\n--- Phase 3 Verification Complete! ---")

if __name__ == "__main__":
    asyncio.run(verify_checkpointing())
