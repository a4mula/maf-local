"""
Unit Tests for TLB Workflow

Tests for Tactical Level Batcher workflow orchestration.
Validates parallel execution, report aggregation, and error handling.
"""

import pytest
from agent_framework import AgentThread
from src.workflows.tlb_workflow import TLBWorkflow
from src.agents.executors import CoderExecutor, TesterExecutor, WriterExecutor
from src.clients.litellm_client import LiteLLMChatClient
from src.config.settings import settings
from src.models.data_contracts import ExecutorReport


@pytest.fixture
def chat_client():
    """Create LiteLLM chat client for testing."""
    return LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)


@pytest.fixture
def executors(chat_client):
    """Create executor instances for TLB."""
    return {
        "coder": CoderExecutor(chat_client=chat_client),
        "tester": TesterExecutor(chat_client=chat_client),
        "writer": WriterExecutor(chat_client=chat_client)
    }


@pytest.fixture
def tlb_workflow(executors):
    """Create TLB workflow instance."""
    return TLBWorkflow(executors=executors)


class TestTLBWorkflowCreation:
    """Tests for TLB workflow creation and configuration."""
    
    def test_tlb_creation(self, tlb_workflow):
        """TLB should be created successfully with executors."""
        assert tlb_workflow is not None
        assert tlb_workflow.executors is not None
        assert "coder" in tlb_workflow.executors
        assert "tester" in tlb_workflow.executors
        assert "writer" in tlb_workflow.executors


class TestTLBSingleExecutor:
    """Tests for TLB with single executor task."""
    
    @pytest.mark.asyncio
    async def test_tlb_executes_single_coder_task(self, tlb_workflow):
        """TLB should execute a single Coder task successfully."""
        thread = AgentThread()
        tasks = [
            {
                "task_id": "task_001",
                "description": "Create a function that adds two numbers",
                "executor_type": "coder"
            }
        ]
        
        result = await tlb_workflow.execute_tasks(tasks, thread)
        
        assert result is not None
        assert result["total_tasks"] == 1
        assert "reports" in result
        assert len(result["reports"]) == 1
        
        report = result["reports"][0]
        assert isinstance(report, ExecutorReport)
        assert report.executor_task_id == "task_001"
        assert report.status in ["Completed", "Failed"]
        
    @pytest.mark.asyncio
    async def test_tlb_handles_empty_task_list(self, tlb_workflow):
        """TLB should handle empty task list gracefully."""
        thread = AgentThread()
        tasks = []
        
        result = await tlb_workflow.execute_tasks(tasks, thread)
        
        assert result is not None
        assert result["total_tasks"] == 0
        assert result["completed"] == 0
        assert result["failed"] == 0
        assert len(result["reports"]) == 0


class TestTLBMultipleExecutors:
    """Tests for TLB with multiple executor tasks."""
    
    @pytest.mark.asyncio
    async def test_tlb_executes_multiple_tasks(self, tlb_workflow):
        """TLB should execute multiple tasks and aggregate reports."""
        thread = AgentThread()
        tasks = [
            {
                "task_id": "task_001",
                "description": "Create add function",
                "executor_type": "coder"
            },
            {
                "task_id": "task_002",
                "description": "Create test for add function",
                "executor_type": "tester"
            },
            {
                "task_id": "task_003",
                "description": "Document add function",
                "executor_type": "writer"
            }
        ]
        
        result = await tlb_workflow.execute_tasks(tasks, thread)
        
        assert result["total_tasks"] == 3
        assert len(result["reports"]) == 3
        
        # Check each report
        task_ids = [r.executor_task_id for r in result["reports"]]
        assert "task_001" in task_ids
        assert "task_002" in task_ids
        assert "task_003" in task_ids
        
    @pytest.mark.asyncio
    async def test_tlb_aggregates_success_and_failure(self, tlb_workflow):
        """TLB should correctly count completed and failed tasks."""
        thread = AgentThread()
        tasks = [
            {
                "task_id": "task_001",
                "description": "Simple task",
                "executor_type": "coder"
            },
            {
                "task_id": "task_002",
                "description": "Task with unknown executor",
                "executor_type": "unknown_type"  # Should fail
            }
        ]
        
        result = await tlb_workflow.execute_tasks(tasks, thread)
        
        assert result["total_tasks"] == 2
        # At least one should fail (the unknown executor)
        assert result["failed"] >= 1
        
        # Check unknown executor produced failed report
        unknown_report = next(
            (r for r in result["reports"] if r.executor_task_id == "task_002"),
            None
        )
        assert unknown_report is not None
        assert unknown_report.status == "Failed"
        assert "Unknown executor type" in unknown_report.error_message


class TestTLBReportAggregation:
    """Tests for TLB report aggregation logic."""
    
    @pytest.mark.asyncio
    async def test_tlb_includes_execution_time(self, tlb_workflow):
        """TLB should track total execution time."""
        thread = AgentThread()
        tasks = [
            {
                "task_id": "task_001",
                "description": "Quick task",
                "executor_type": "coder"
            }
        ]
        
        result = await tlb_workflow.execute_tasks(tasks, thread)
        
        assert "execution_time_ms" in result
        assert result["execution_time_ms"] >= 0
        
    @pytest.mark.asyncio
    async def test_tlb_calculates_success_rate(self, tlb_workflow):
        """TLB should calculate success rate correctly."""
        thread = AgentThread()
        tasks = [
            {
                "task_id": "task_001",
                "description": "Task 1",
                "executor_type": "coder"
            }
        ]
        
        result = await tlb_workflow.execute_tasks(tasks, thread)
        
        assert "success_rate" in result
        assert 0.0 <= result["success_rate"] <= 1.0
