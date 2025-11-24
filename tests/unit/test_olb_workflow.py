"""
Unit Tests for OLB Workflow

Tests for Orchestration Level Batcher workflow.
Validates routing of StrategicPlan tasks to correct Domain Leads.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agent_framework import AgentThread
from src.workflows.olb_workflow import OLBWorkflow
from src.agents.domain_leads import BaseDomainLead
from src.models.data_contracts import StrategicPlan, TaskDefinition


@pytest.fixture
def mock_dev_dl():
    """Create mock Dev Domain Lead."""
    dl = MagicMock(spec=BaseDomainLead)
    dl.name = "DevDomainLead"
    dl.execute_task = AsyncMock(return_value={
        "task_id": "task_001",
        "status": "Completed",
        "summary": "Mock execution success"
    })
    return dl


@pytest.fixture
def mock_qa_dl():
    """Create mock QA Domain Lead."""
    dl = MagicMock(spec=BaseDomainLead)
    dl.name = "QADomainLead"
    dl.execute_task = AsyncMock(return_value={
        "task_id": "task_002",
        "status": "Completed",
        "summary": "Mock QA success"
    })
    return dl


@pytest.fixture
def olb_workflow(mock_dev_dl, mock_qa_dl):
    """Create OLB workflow with mock DLs."""
    domain_leads = {
        "Development": mock_dev_dl,
        "QA": mock_qa_dl
    }
    return OLBWorkflow(domain_leads=domain_leads)


class TestOLBWorkflow:
    """Tests for OLB workflow logic."""
    
    @pytest.mark.asyncio
    async def test_olb_routes_tasks_correctly(self, olb_workflow, mock_dev_dl, mock_qa_dl):
        """OLB should route tasks to correct DL based on domain."""
        thread = AgentThread()
        plan = StrategicPlan(
            plan_id="plan_001",
            target_domains=["Development", "QA"],
            tasks=[
                TaskDefinition(
                    task_id="task_001",
                    domain="Development",
                    description="Dev task"
                ),
                TaskDefinition(
                    task_id="task_002",
                    domain="QA",
                    description="QA task"
                )
            ]
        )
        
        result = await olb_workflow.execute_plan(plan, thread)
        
        # Verify routing
        mock_dev_dl.execute_task.assert_called_once()
        mock_qa_dl.execute_task.assert_called_once()
        
        # Verify result aggregation
        assert result["status"] == "Completed"
        assert result["total_tasks"] == 2
        assert result["completed"] == 2
        assert len(result["results"]) == 2
        
    @pytest.mark.asyncio
    async def test_olb_handles_missing_dl(self, olb_workflow):
        """OLB should handle tasks for unknown domains gracefully."""
        thread = AgentThread()
        plan = StrategicPlan(
            plan_id="plan_002",
            target_domains=["Unknown"],
            tasks=[
                TaskDefinition(
                    task_id="task_003",
                    domain="UnknownDomain",
                    description="Mystery task"
                )
            ]
        )
        
        result = await olb_workflow.execute_plan(plan, thread)
        
        assert result["status"] == "Failed"
        assert result["failed"] == 1
        assert len(result["failed_details"]) == 1
        assert "No Domain Lead found" in result["failed_details"][0]["error"]
        
    @pytest.mark.asyncio
    async def test_olb_stops_on_failure(self, olb_workflow, mock_dev_dl):
        """OLB should stop execution if a task fails."""
        # Setup Dev DL to fail
        mock_dev_dl.execute_task = AsyncMock(return_value={
            "task_id": "task_fail",
            "status": "Failed",
            "error": "Execution failed"
        })
        
        thread = AgentThread()
        plan = StrategicPlan(
            plan_id="plan_003",
            target_domains=["Development", "QA"],
            tasks=[
                TaskDefinition(
                    task_id="task_fail",
                    domain="Development",
                    description="Failing task"
                ),
                TaskDefinition(
                    task_id="task_next",
                    domain="QA",
                    description="Should not run"
                )
            ]
        )
        
        result = await olb_workflow.execute_plan(plan, thread)
        
        assert result["status"] == "Failed"
        assert result["completed"] == 0
        assert result["failed"] == 1
        
        # QA DL should NOT have been called
        olb_workflow.domain_leads["QA"].execute_task.assert_not_called()
