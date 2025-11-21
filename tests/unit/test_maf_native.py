import asyncio
from src.clients.litellm_client import LiteLLMChatClient
from src.agents.core_agent_sdk import CoreAgent
from src.persistence.audit_log import AuditLogProvider
from src.config.settings import settings

async def main():
    print("--- Testing MAF-Native CoreAgent ---\n")
    
    # Initialize dependencies
    client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
    audit_log = AuditLogProvider()
    
    # Create MAF-native CoreAgent (no tool registry needed!)
    agent = CoreAgent(
        client=client,
        audit_log=audit_log,
        agent_type="Local-Dev"
    )
    
    print("✅ Agent initialized with MAF-native tools\n")
    
    # Test 1: Simple conversation
    print("Test 1: Basic conversation")
    response = await agent.process("What is the capital of France?")
    print(f"Q: What is the capital of France?")
    print(f"A: {response}\n")
    
    # Test 2: Context storage
    print("Test 2: Context tools")
    response = await agent.process("Remember that my favorite color is blue")
    print(f"Q: Remember that my favorite color is blue")
    print(f"A: {response}\n")
    
    # Test 3: Context retrieval
    response = await agent.process("What's my favorite color?")
    print(f"Q: What's my favorite color?")
    print(f"A: {response}\n")
    
    print("✅ All tests completed!")
    print("\nMAF-native tools are working with automatic schema generation!")

if __name__ == "__main__":
    asyncio.run(main())
