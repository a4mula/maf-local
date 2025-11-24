"""
Integration Tests for Domain Lead Tier

Tests the full flow from Domain Lead -> TLB -> Executors.
Verifies that a high-level task is correctly broken down and executed.
"""

import pytest
from agent_framework import AgentThread
from src.agents.domain_leads import DevDomainLead
from src.workflows.tlb_workflow import TLBWorkflow
from src.agents.executors import CoderExecutor, TesterExecutor, WriterExecutor
from src.clients.litellm_client import LiteLLMChatClient
from src.config.settings import settings
from src.models.data_contracts import TaskDefinition


@pytest.fixture
def chat_client():
    """Create LiteLLM chat client."""
    return LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)


@pytest.fixture
def executors(chat_client):
    """Create real executors."""
    return {
        "coder": CoderExecutor(chat_client=chat_client),
        "tester": TesterExecutor(chat_client=chat_client),
        "writer": WriterExecutor(chat_client=chat_client)
    }


@pytest.fixture
def tlb_workflow(executors):
    """Create real TLB workflow."""
    return TLBWorkflow(executors=executors)


@pytest.fixture
def dev_dl(chat_client, tlb_workflow):
    """Create real DevDomainLead."""
    return DevDomainLead(chat_client=chat_client, tlb_workflow=tlb_workflow)


class TestDomainLeadIntegration:
    """Integration tests for Domain Lead flow."""
    
    @pytest.mark.asyncio
    async def test_dev_dl_full_execution_flow(self, dev_dl):
        """DevDL should break down task and execute via real TLB/Executors."""
        thread = AgentThread()
        task_def = TaskDefinition(
            task_id="integ_001",
            domain="Development",
            description="Create a Python function 'multiply(a, b)' that returns the product.",
            assigned_to="DevDL"
        )
        
        print("\n[Integration] Starting DevDL execution flow...")
        result = await dev_dl.execute_task(task_def, thread)
        
        print(f"[Integration] Result status: {result['status']}")
        print(f"[Integration] Summary: {result['summary']}")
        
        if result["status"] == "Failed":
            print("\n[Integration] Failure Details:")
            for report in result["tlb_result"]["reports"]:
                if report.status == "Failed":
                    print(f"  - Task {report.executor_task_id} ({report.executor_name}): {report.error_message}")
        
        # Verify success
        assert result["status"] == "Completed"
        assert result["tlb_result"]["total_tasks"] > 0
        assert result["tlb_result"]["completed"] > 0
        assert result["tlb_result"]["failed"] == 0
        
        # Verify artifacts were produced
        reports = result["tlb_result"]["reports"]
        artifacts = [r.outputs.get("artifact") for r in reports if r.status == "Completed"]
        assert len(artifacts) > 0
        
        # Check for code artifact
        code_artifact = next((a for a in artifacts if "def multiply" in a or "return" in a), None)
        assert code_artifact is not None, "No code artifact found"
