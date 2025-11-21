import asyncio
from src.clients.litellm_client import LiteLLMChatClient
from src.agents.core_agent_sdk import CoreAgent
from src.persistence.audit_log import AuditLogProvider
from src.persistence.message_store import MessageStoreProvider
from src.config.tool_registry import TOOL_REGISTRY

async def main():
    print("--- Verifying SDK-based CoreAgent ---")
    
    # 1. Initialize dependencies
    client = LiteLLMChatClient(model_name="maf-ollama/llama3.1")
    audit_log = AuditLogProvider()
    message_store = MessageStoreProvider()
    
    # 2. Get tools for Local-Dev agent
    tools = TOOL_REGISTRY.get("Local-Dev", [])
    
    # 3. Create SDK-based CoreAgent
    agent = CoreAgent(
        client=client,
        audit_log=audit_log,
        message_store=message_store,
        registered_tools=tools,
        agent_type="Local-Dev"
    )
    
    # 4. Test basic conversation
    print("\nTesting basic conversation...")
    response = await agent.process("What is the capital of France? Answer in one word.")
    print(f"Response: {response}")
    
    if "Paris" in response or "paris" in response.lower():
        print("\n✅ SUCCESS: SDK-based CoreAgent is working!")
    else:
        print(f"\n⚠️  Got response but unexpected content.")

if __name__ == "__main__":
    asyncio.run(main())
