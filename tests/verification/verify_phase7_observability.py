import asyncio
import httpx
import time
from src.services.metrics_service import MetricsService
from src.persistence.audit_log import AuditLogProvider

async def verify_observability():
    print("--- Verifying Phase 7: Observability ---")

    # 1. Start Metrics Server
    print("[1] Starting Metrics Server...")
    MetricsService().start_server(8002) # Use different port for test
    
    # 2. Generate some metrics via AuditLog
    print("[2] Generating Metrics...")
    audit_log = AuditLogProvider()
    
    # We mock the DB connection to avoid needing actual DB for this unit test
    # Or we just call record_action directly if we want to test just the metrics service
    # But let's try to use the audit log wrapper if possible. 
    # Since AuditLog connects to DB, and DB might be running, let's try.
    # If DB fails, AuditLog catches exception and records error metric.
    
    await audit_log.log("TestAgent", "TEST_ACTION", "Testing metrics")
    await audit_log.log("TestAgent", "TEST_ACTION", "Testing metrics again")
    
    # 3. Query Metrics Endpoint
    print("[3] Querying Metrics Endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8002/metrics")
            metrics_text = response.text
            
            print(f"   Response Status: {response.status_code}")
            
            if "maf_agent_actions_total" in metrics_text:
                print("✅ Found 'maf_agent_actions_total' metric")
            else:
                print("❌ 'maf_agent_actions_total' metric NOT found")
                
            if 'agent_name="TestAgent"' in metrics_text:
                print("✅ Found correct label 'TestAgent'")
            else:
                print("❌ Label 'TestAgent' NOT found")
                
        except Exception as e:
            print(f"❌ Failed to query metrics: {e}")

    print("--- Phase 7 Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_observability())
