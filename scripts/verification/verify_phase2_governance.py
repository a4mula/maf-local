import asyncio
import os
from src.services.agent_factory import AgentFactory
from src.persistence.maf_message_store import PostgreSQLMessageStore
from src.config.settings import settings

async def verify_governance():
    print("--- Verifying Phase 2: Governance Layer ---")
    
    # 1. Initialize DB Store
    print("[1] Initializing PostgreSQL Store...")
    store = PostgreSQLMessageStore(settings.DATABASE_URL)
    await store._init_db()
    
    # 2. Create Hierarchy (injecting store)
    print("[2] Creating Agent Hierarchy...")
    hierarchy = AgentFactory.create_hierarchy(message_store=store)
    project_lead = hierarchy["project_lead"]
    governance = hierarchy["dependencies"]["governance"]
    
    # 3. Test Project Lead -> Governance Flow
    print("[3] Testing Decision Storage...")
    idea = "We should implement a 4-tier agent hierarchy."
    response = await project_lead.receive_idea(idea)
    print(f"Project Lead Response: {response}")
    
    # 4. Verify Decision in DB
    print("[4] Verifying Decision Persistence...")
    decisions = await governance.get_all_decisions()
    if len(decisions) > 0:
        d = decisions[-1]
        print(f"✅ Decision found: {d.id}")
        print(f"   Category: {d.category}")
        print(f"   Content: {d.content}")
        print(f"   Created By: {d.created_by}")
    else:
        print("❌ No decisions found!")
        exit(1)
        
    # 5. Test Drift Detection
    print("[5] Testing Drift Detection...")
    # Simulate a state that matches
    current_state_match = {"vision": {"idea": idea}}
    drift = await governance.check_drift(current_state_match)
    if not drift:
        print("✅ No drift detected for matching state.")
    else:
        print(f"❌ Unexpected drift: {drift}")
        
    # Simulate a state that drifts
    current_state_drift = {"vision": {"idea": "Something else"}}
    drift = await governance.check_drift(current_state_drift)
    if drift:
        print(f"✅ Drift detected correctly: {drift[0]}")
    else:
        print("❌ Drift NOT detected when it should have been!")
        
    print("\n--- Phase 2 Verification Complete! ---")

if __name__ == "__main__":
    asyncio.run(verify_governance())
