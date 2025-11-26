"""
Integration Tests for OLB Edge Cases
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.workflows.olb_workflow import OLBWorkflow
from src.models.data_contracts import StrategicPlan, TaskDefinition

@pytest.fixture
def mock_project_lead():
    """Mock ProjectLeadAgent."""
    pl = MagicMock()
    # Mock create_plan response
    pl.create_plan = AsyncMock()
    return pl

@pytest.fixture
def mock_domain_leads():
    """Mock Domain Leads."""
    return {
        "Frontend": MagicMock(),
        "Backend": MagicMock(),
        "QA": MagicMock()
    }

@pytest.fixture
def olb_workflow(mock_domain_leads):
    """Create OLBWorkflow instance."""
    return OLBWorkflow(domain_leads=mock_domain_leads)

class TestOLBEdgeCases:
    
    @pytest.mark.asyncio
    async def test_route_ambiguous_domain(self, olb_workflow):
        """Should handle tasks with ambiguous domains."""
        from agent_framework import AgentThread
        
        # Setup plan with unknown domain
        plan = StrategicPlan(
            plan_id="plan_ambiguous",
            target_domains=["Unknown"],
            tasks=[
                TaskDefinition(
                    task_id="t1",
                    domain="Unknown",
                    description="Do something mysterious"
                )
            ]
        )
        
        thread = AgentThread()
        
        # Execute
        result = await olb_workflow.execute_plan(plan, thread)
        
        # Verify
        # The implementation logs error and marks task as Failed
        assert result["status"] == "Failed"
        assert result["failed"] == 1
        assert result["failed_details"][0]["task_id"] == "t1"
        assert "No Domain Lead found" in result["failed_details"][0]["error"]

    @pytest.mark.asyncio
    async def test_route_mixed_domains(self, olb_workflow, mock_domain_leads):
        """Should correctly route mixed domain tasks."""
        from agent_framework import AgentThread
        
        plan = StrategicPlan(
            plan_id="plan_mixed",
            target_domains=["Frontend", "Backend"],
            tasks=[
                TaskDefinition(task_id="t1", domain="Frontend", description="UI"),
                TaskDefinition(task_id="t2", domain="Backend", description="API")
            ]
        )
        
        # Mock domain lead execution
        mock_domain_leads["Frontend"].execute_task = AsyncMock(return_value={"status": "Completed"})
        mock_domain_leads["Backend"].execute_task = AsyncMock(return_value={"status": "Completed"})
        
        thread = AgentThread()
        result = await olb_workflow.execute_plan(plan, thread)
        
        assert result["status"] == "Completed"
        mock_domain_leads["Frontend"].execute_task.assert_called_once()
        mock_domain_leads["Backend"].execute_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_plan(self, olb_workflow):
        """Should handle empty plan gracefully."""
        from agent_framework import AgentThread
        
        plan = StrategicPlan(
            plan_id="plan_empty",
            target_domains=[],
            tasks=[]
        )
        
        thread = AgentThread()
        result = await olb_workflow.execute_plan(plan, thread)
        
        assert result["status"] == "Completed"
        assert result["total_tasks"] == 0
