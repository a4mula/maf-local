import asyncio
from src.agents.context_retrieval_agent import ContextRetrievalAgent
from src.clients.litellm_client import LiteLLMChatClient

async def verify_context_retrieval():
    print("--- Verifying Phase 4: Context Management ---")
    
    # 1. Initialize Agent
    print("[1] Initializing ContextRetrievalAgent...")
    client = LiteLLMChatClient()
    agent = ContextRetrievalAgent(client)
    
    if not agent.chroma_client:
        print("❌ Failed to initialize ChromaDB client. Is the service running?")
        exit(1)
        
    # 2. Store Knowledge
    print("[2] Storing Knowledge...")
    fact = "The MAF framework prioritizes FOSS-first principles and the Principle of Least Authority."
    result = await agent.add_knowledge(fact, {"category": "principles"})
    print(f"   Store Result: {result}")
    
    # 3. Query Knowledge
    print("[3] Querying Knowledge...")
    query = "What are the core principles of MAF?"
    results = await agent.query_knowledge(query)
    
    found = False
    for r in results:
        print(f"   Found: {r['content']} (Metadata: {r['metadata']})")
        if "FOSS-first" in r['content']:
            found = True
            
    if found:
        print("✅ Successfully retrieved relevant context.")
    else:
        print("❌ Failed to retrieve relevant context.")
        exit(1)

    print("\n--- Phase 4 Verification Complete! ---")

if __name__ == "__main__":
    asyncio.run(verify_context_retrieval())
