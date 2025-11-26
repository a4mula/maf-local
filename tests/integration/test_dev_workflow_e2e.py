"""
Integration Tests for Dev Domain Workflow (E2E)

Validates the complete flow from Project Lead -> DevDomainLead -> Executors.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.workflows.olb_workflow import OLBWorkflow
from src.workflows.tlb_workflow import TLBWorkflow
from src.agents.domain_leads.dev_domain_lead import DevDomainLead
from src.models.data_contracts import StrategicPlan, TaskDefinition, ExecutorReport
from agent_framework import AgentThread

@pytest.fixture
def mock_chat_client():
    """Mock ChatClient for DevDomainLead decomposition."""
    client = MagicMock()
    
    # Mock response for _break_down_task
    # DevDomainLead expects a JSON list of subtasks
    subtasks = [
        {
            "description": "Implement the feature",
            "executor_type": "coder",
            "task_id": "t1_sub1"
        },
        {
            "description": "Test the feature",
            "executor_type": "tester",
            "task_id": "t1_sub2"
        }
    ]
    
    response = MagicMock()
    response.text = json.dumps(subtasks)
    
    # Configure run method (inherited from ChatAgent)
    # Note: BaseDomainLead calls self.run(), which usually calls client.get_response()
    # But since we are mocking the client passed to __init__, we need to ensure
    # the agent uses it correctly. 
    # However, ChatAgent.run() is what we need to mock if we want to avoid real network calls.
    # But we can't easily mock the method on the instance before it's created if we use the real class.
    # So we'll mock the client and assume ChatAgent uses it.
    
    # Actually, ChatAgent.run is async. We should mock the client's async method.
    # Assuming ChatAgent calls client.get_response(messages, ...)
    client.get_response = AsyncMock(return_value=response)
    
    return client

@pytest.fixture
def mock_executors():
    """Mock Executors for TLB."""
    coder = MagicMock()
    coder.execute_task = AsyncMock(return_value=ExecutorReport(
        executor_task_id="t1_sub1",
        executor_name="CoderExecutor",
        status="Completed",
        outputs={"file": "feature.py"},
        duration_ms=100
    ))
    
    tester = MagicMock()
    tester.execute_task = AsyncMock(return_value=ExecutorReport(
        executor_task_id="t1_sub2",
        executor_name="TesterExecutor",
        status="Completed",
        outputs={"test_file": "test_feature.py"},
        duration_ms=100
    ))
    
    return {
        "coder": coder,
        "tester": tester
    }

@pytest.fixture
def tlb_workflow(mock_executors):
    """Real TLBWorkflow with mock executors."""
    return TLBWorkflow(executors=mock_executors)

@pytest.fixture
def dev_domain_lead(mock_chat_client, tlb_workflow):
    """Real DevDomainLead with mock client and TLB."""
    agent = DevDomainLead(chat_client=mock_chat_client, tlb_workflow=tlb_workflow)
    
    # Patch the run method to avoid using the real ChatAgent.run logic
    # which might try to construct messages and call the client.
    # We just want it to return our JSON response.
    response = MagicMock()
    response.text = mock_chat_client.get_response.return_value.text
    agent.run = AsyncMock(return_value=response)
    
    return agent

@pytest.fixture
def olb_workflow(dev_domain_lead):
    """Real OLBWorkflow with real DevDomainLead."""
    return OLBWorkflow(domain_leads={"Development": dev_domain_lead})

@pytest.mark.asyncio
async def test_dev_workflow_complete(olb_workflow, mock_executors, dev_domain_lead):
    """
    Test full development workflow end-to-end:
    ProjectLead (Plan) -> OLB -> DevDomainLead -> TLB -> Executors
    """
    # 1. Create strategic plan targeting Development domain
    plan = StrategicPlan(
        plan_id="plan_dev_e2e",
        target_domains=["Development"],
        tasks=[
            TaskDefinition(
                task_id="t1",
                domain="Development",
                description="Implement a new feature"
            )
        ]
    )
    
    thread = AgentThread()
    
    # 2. Execute Workflow
    result = await olb_workflow.execute_plan(plan, thread)
    
    # 3. Verify Results
    assert result["status"] == "Completed"
    assert result["completed"] == 1
    assert result["failed"] == 0
    
    # 4. Verify DevDomainLead interaction
    # Should have called run() to decompose task
    dev_domain_lead.run.assert_called_once()
    
    # 5. Verify Executors were called
    mock_executors["coder"].execute_task.assert_called_once()
    mock_executors["tester"].execute_task.assert_called_once()
    
    # Verify task details passed to executors
    coder_call = mock_executors["coder"].execute_task.call_args[0][0]
    assert coder_call["executor_type"] == "coder"
    assert coder_call["task_id"] == "t1_sub1"
    
    tester_call = mock_executors["tester"].execute_task.call_args[0][0]
    assert tester_call["executor_type"] == "tester"
    assert tester_call["task_id"] == "t1_sub2"
