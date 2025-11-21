#!/usr/bin/env python3
"""
Test script for SDK-based CoreAgent in interactive mode.
Run from project root with: .venv/bin/python3 test_sdk_main.py
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from src.clients.litellm_client import LiteLLMChatClient
from src.agents.core_agent_sdk import CoreAgent
from src.persistence.audit_log import AuditLogProvider
from src.persistence.message_store import MessageStoreProvider
from src.config.tool_registry import TOOL_REGISTRY
from src.config.settings import settings

async def main():
    print("--- Testing SDK-based CoreAgent ---")
    
    # Initialize dependencies
    client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
    audit_log = AuditLogProvider()
    message_store = MessageStoreProvider()
    
    # Get tools
    agent_tools = [t.model_dump() for t in TOOL_REGISTRY.get("Local-Dev", [])]
    
    # Create SDK agent
    agent = CoreAgent(
        client=client,
        audit_log=audit_log,
        message_store=message_store,
        registered_tools=agent_tools,
        agent_type="Local-Dev"
    )
    
    print("\\n✅ Agent initialized successfully!")
    print("\\nTesting conversation...")
    
    # Test 1: Simple question
    response = await agent.process("What is the capital of France?")
    print(f"Q: What is the capital of France?")
    print(f"A: {response}")
    
    # Test 2: Math question
    response2 = await agent.process("What is 15 + 27?")
    print(f"\\nQ: What is 15 + 27?")
    print(f"A: {response2}")
    
    print("\\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
