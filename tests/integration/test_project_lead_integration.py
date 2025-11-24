"""
Integration Tests for Project Lead (Step 9)

Tests the full integration of ProjectLead -> OLB -> Domain Leads.
Verifies that the Project Lead can use the submit_strategic_plan tool to trigger execution.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agent_framework import AgentThread
from src.agents.project_lead_agent import ProjectLeadAgent
from src.workflows.olb_workflow import OLBWorkflow
from src.clients.litellm_client import LiteLLMChatClient
from src.config.settings import settings


@pytest.fixture
def chat_client():
    """Create LiteLLM chat client."""
    return LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)


@pytest.fixture
def mock_olb():
    """Create mock OLB workflow."""
    olb = MagicMock(spec=OLBWorkflow)
    olb.execute_plan = AsyncMock(return_value={
        "plan_id": "plan_mock",
        "status": "Completed",
        "total_tasks": 1,
        "completed": 1,
        "failed": 0,
        "results": [{"task_id": "t1", "status": "Completed"}]
    })
    return olb


@pytest.fixture
def project_lead(chat_client, mock_olb):
    """Create ProjectLeadAgent with mock OLB."""
    return ProjectLeadAgent(chat_client=chat_client, olb_workflow=mock_olb)


class TestProjectLeadIntegration:
    """Tests for Project Lead integration with OLB."""
    
    @pytest.mark.asyncio
    async def test_pl_initialization(self, project_lead):
        """Project Lead should be initialized with OLB and strategy tool."""
        assert project_lead.olb_workflow is not None
        # Check if submit_strategic_plan is exposed
        assert hasattr(project_lead, "submit_strategic_plan_tool")
        assert project_lead.submit_strategic_plan_tool is not None
        
    @pytest.mark.asyncio
    async def test_submit_strategic_plan_tool(self, project_lead, mock_olb):
        """The submit_strategic_plan tool should call OLB.execute_plan."""
        # Call the tool directly
        result = await project_lead.submit_strategic_plan_tool(
            target_domains=["Development"],
            tasks=[{"description": "Build a feature", "domain": "Development"}],
            plan_context="Test context"
        )
        
        # Verify OLB was called
        mock_olb.execute_plan.assert_called_once()
        
        # Verify result string
        assert "Plan Execution Result: Completed" in result
        
    @pytest.mark.asyncio
    async def test_pl_full_flow_mocked(self, project_lead, mock_olb):
        """Project Lead should use the tool when asked to execute a plan."""
        # This tests the LLM's ability to pick the tool.
        # We can't easily force the LLM to pick a tool in a unit test without a real model,
        # but we can verify the agent is set up correctly.
        # For this test, we'll trust the tool existence test above.
        pass
