import asyncio
import logging
from src.clients.litellm_client import LiteLLMChatClient
from src.agents.core_agent_sdk import CoreAgent
from src.persistence.audit_log import AuditLogProvider
from src.config.settings import settings

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def main():
    print("--- Testing Tool Execution with Debug Logging ---\n")
    
    # Initialize dependencies
    client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
    audit_log = AuditLogProvider()
    
    # Create agent
    agent = CoreAgent(
        client=client,
        audit_log=audit_log,
        agent_type="Local-Dev"
    )
    
    print("✅ Agent initialized\n")
    
    # Test tool execution
    print("Test: Search for capital of France")
    response = await agent.process("Search the web for the capital of France")
    print(f"Response: {response}\n")
    print(f"Response type: {type(response)}")
    print(f"Response length: {len(response)}")

if __name__ == "__main__":
    asyncio.run(main())
