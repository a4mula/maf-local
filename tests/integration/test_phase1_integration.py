"""
Integration tests for Phase 1 U.B.E. implementation

Tests:
- Agent factory creates DocumentationAgent
- ProjectLeadAgent MAF compliance (inherits from ChatAgent)
- A2A communication between ProjectLead and DocumentationAgent (future)
"""

import pytest
from src.services.agent_factory import AgentFactory
from src.agents.project_lead_agent import ProjectLeadAgent
from src.agents.documentation_agent import DocumentationAgent
from agent_framework import ChatAgent


class TestAgentFactory:
    """Test agent factory creates all Phase 1 agents."""
    
    def test_factory_creates_documentation_agent(self):
        """Test that factory creates DocumentationAgent."""
        hierarchy = AgentFactory.create_hierarchy()
        
        assert "documentation_agent" in hierarchy
        assert isinstance(hierarchy["documentation_agent"], DocumentationAgent)
        assert hierarchy["documentation_agent"] is not None
    
    def test_factory_creates_project_lead(self):
        """Test that factory creates ProjectLeadAgent."""
        hierarchy = AgentFactory.create_hierarchy()
        
        assert "project_lead" in hierarchy
        assert isinstance(hierarchy["project_lead"], ProjectLeadAgent)
    
    def test_factory_creates_liaison(self):
        """Test that factory creates LiaisonAgent."""
        hierarchy = AgentFactory.create_hierarchy()
        
        assert "liaison" in hierarchy
        assert hierarchy["liaison"] is not None
    
    def test_phase1_hierarchy_structure(self):
        """Test that Phase 1 hierarchy has correct structure."""
        hierarchy = AgentFactory.create_hierarchy()
        
        # Phase 1 should have Tier 1 + Tier 2
        assert "liaison" in hierarchy  # Tier 1
        assert "project_lead" in hierarchy  # Tier 2
        assert "documentation_agent" in hierarchy  # Tier 2
        
        # Phase 2 agents should be empty
        assert hierarchy["domain_leads"] == {}
        assert hierarchy["executors"] == {}


class TestProjectLeadAgentCompliance:
    """Test ProjectLeadAgent MAF compliance."""
    
    def test_project_lead_inherits_from_chat_agent(self):
        """Test that ProjectLeadAgent properly inherits from ChatAgent."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        pl_agent = ProjectLeadAgent(chat_client=client)
        
        # Critical: ProjectLeadAgent must inherit from ChatAgent
        assert isinstance(pl_agent, ChatAgent)
    
    def test_project_lead_has_run_method(self):
        """Test that ProjectLeadAgent has inherited run() method."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        pl_agent = ProjectLeadAgent(chat_client=client)
        
        # Should have inherited run() method from ChatAgent
        assert hasattr(pl_agent, 'run')
        assert callable(pl_agent.run)


class TestDocumentationAgent:
    """Test DocumentationAgent functionality."""
    
    def test_documentation_agent_is_chat_agent(self):
        """Test that DocumentationAgent inherits from ChatAgent."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        doc_agent = DocumentationAgent(chat_client=client)
        
        assert isinstance(doc_agent, ChatAgent)
    
    def test_documentation_agent_has_provide_context_method(self):
        """Test that DocumentationAgent has provide_context method."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        doc_agent = DocumentationAgent(chat_client=client)
        
        assert hasattr(doc_agent, 'provide_context')
        assert callable(doc_agent.provide_context)
    
    def test_documentation_agent_has_approve_file_write_method(self):
        """Test that DocumentationAgent has approve_file_write method."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        doc_agent = DocumentationAgent(chat_client=client)
        
        assert hasattr(doc_agent, 'approve_file_write')
        assert callable(doc_agent.approve_file_write)
    
    @pytest.mark.asyncio
    async def test_approve_file_write_authorizes_project_lead(self):
        """Test that DocumentationAgent approves file writes from ProjectLead."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        doc_agent = DocumentationAgent(chat_client=client)
        
        approval = await doc_agent.approve_file_write(
            requesting_agent="ProjectLeadAgent",
            file_path="/app/test.py",
            reason="Test file creation"
        )
        
        assert approval["approved"] is True
        assert "ProjectLeadAgent" in approval["reason"]
    
    @pytest.mark.asyncio
    async def test_approve_file_write_denies_unauthorized_agent(self):
        """Test that DocumentationAgent denies file writes from unauthorized agents."""
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        doc_agent = DocumentationAgent(chat_client=client)
        
        approval = await doc_agent.approve_file_write(
            requesting_agent="MaliciousAgent",
            file_path="/app/malicious.py",
            reason="Unauthorized access"
        )
        
        assert approval["approved"] is False
        assert "Unauthorized" in approval["reason"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
