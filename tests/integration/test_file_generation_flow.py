import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock
from src.services.agent_factory import AgentFactory

@pytest.mark.asyncio
async def test_file_generation_flow():
    """
    Verifies the full MVP flow structure:
    User -> Liaison -> ProjectLead (ChatAgent with @use_function_invocation)
    
    Note: Full end-to-end file generation requires real LLM interaction.
    This test verifies the agent structure is correctly wired.
    """
    # Use the REAL AgentFactory to ensure tools are wired correctly
    hierarchy = AgentFactory.create_hierarchy()
    
    # Verify structure
    assert "liaison" in hierarchy
    assert "project_lead" in hierarchy
    
    liaison = hierarchy["liaison"]
    project_lead = hierarchy["project_lead"]
    
    # Verify ProjectLeadAgent has ChatAgent with tools
    assert hasattr(project_lead, 'sdk_agent')
    assert project_lead.sdk_agent is not None
    
    # Verify tools are registered
    from src.tools.universal_tools import registry
    tools = registry.get_ai_functions()
    assert len(tools) > 0, "Tools should be registered"
    
    # Verify write_file tool exists
    tool_names = [tool.name for tool in tools]
    assert "write_file" in tool_names, "write_file tool should be registered"
    
    print("File generation flow structure verified!")
    print(f"Registered tools: {tool_names}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_file_generation_flow())
