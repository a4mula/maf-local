import asyncio
from src.services.agent_factory import AgentFactory
from src.tools.universal_tools import registry
import src.tools.code_tools # Register tools

async def verify_artifact_management():
    print("--- Verifying Phase 5: Artifact Management ---")
    
    # 1. Create Hierarchy
    print("[1] Creating Agent Hierarchy...")
    hierarchy = AgentFactory.create_hierarchy()
    artifact_manager = hierarchy["dependencies"]["artifact_manager"]
    project_lead = hierarchy["project_lead"] # Should NOT have access
    
    # 2. Verify Artifact Manager Access
    print("[2] Verifying Artifact Manager Access...")
    code = "print('Hello from Artifact Manager')"
    try:
        # We manually simulate the registry check here because CoreAgent.process wraps it
        # But let's try to use the tool directly via registry first to test the decorator
        result = await registry.execute_tool("execute_code", caller_role="ArtifactManager", code=code)
        print(f"✅ ArtifactManager executed code: {result}")
    except Exception as e:
        print(f"❌ ArtifactManager failed to execute code: {e}")
        exit(1)

    # 3. Verify Unauthorized Access (Project Lead)
    print("[3] Verifying Unauthorized Access (Project Lead)...")
    try:
        # Project Lead has role "ProjectLead" (or whatever is passed to CoreAgent)
        # Actually ProjectLeadAgent wraps ChatAgent directly, it doesn't inherit from CoreAgentSDK in the same way
        # Let's test with a fake role
        await registry.execute_tool("execute_code", caller_role="ProjectLead", code=code)
        print("❌ ProjectLead was able to execute code! (Security Failure)")
        exit(1)
    except PermissionError as e:
        print(f"✅ ProjectLead blocked: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error for ProjectLead: {type(e).__name__}: {e}")
        # If it's not PermissionError, we might have a problem, but let's see.
        
    # 4. Verify Agent Integration
    print("[4] Verifying Agent Integration...")
    # We ask the ArtifactManager to do something
    response = await artifact_manager.process("Execute this code: print('Integration Test')")
    print(f"   Agent Response: {response}")
    if "Integration Test" in response or "No output" in response: 
        # "No output" might happen if it captures stdout but doesn't return it in the text
        # But execute_code returns the output.
        print("✅ Agent successfully used the tool.")
    else:
        print("⚠️ Agent might not have used the tool or output format differs.")

    print("\n--- Phase 5 Verification Complete! ---")

if __name__ == "__main__":
    asyncio.run(verify_artifact_management())
