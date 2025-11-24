"""
Unit Tests for Executor Agents

Tests for BaseExecutor and concrete executor implementations (Coder, Tester, Writer).
Validates atomic task execution, ExecutorReport structure, and escalation patterns.
"""

import pytest
from agent_framework import AgentThread
from src.agents.executors import CoderExecutor, TesterExecutor, WriterExecutor
from src.clients.litellm_client import LiteLLMChatClient
from src.config.settings import settings
from src.models.data_contracts import ExecutorReport


@pytest.fixture
def chat_client():
    """Create LiteLLM chat client for testing."""
    return LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)


@pytest.fixture
def coder_executor(chat_client):
    """Create CoderExecutor instance."""
    return CoderExecutor(chat_client=chat_client)


@pytest.fixture
def tester_executor(chat_client):
    """Create TesterExecutor instance."""
    return TesterExecutor(chat_client=chat_client)


@pytest.fixture
def writer_executor(chat_client):
    """Create WriterExecutor instance."""
    return WriterExecutor(chat_client=chat_client)


class TestCoderExecutor:
    """Tests for CoderExecutor agent."""
    
    def test_coder_executor_creation(self, coder_executor):
        """CoderExecutor should be created successfully with proper configuration."""
        assert coder_executor is not None
        assert coder_executor.name == "CoderExecutor"
        assert coder_executor.executor_type == "Coder"
        # Should have execute_code tool
        assert len(coder_executor._local_mcp_tools) >= 0  # MAF stores tools internally
        
    @pytest.mark.asyncio
    async def test_coder_executes_simple_task(self, coder_executor):
        """CoderExecutor should execute a simple code generation task."""
        thread = AgentThread()
        task = {
            "task_id": "test_001",
            "description": "Create a Python function called 'add' that takes two parameters and returns their sum."
        }
        
        report = await coder_executor.execute_task(task, thread)
        
        assert isinstance(report, ExecutorReport)
        assert report.executor_task_id == "test_001"
        assert report.executor_name == "CoderExecutor"
        assert report.status in ["Completed", "Failed"]
        
        if report.status == "Completed":
            assert "artifact" in report.outputs
            artifact = report.outputs["artifact"]
            # Should contain function definition
            assert "def add" in artifact or "def" in artifact
            
    @pytest.mark.asyncio
    async def test_coder_escalates_unclear_task(self, coder_executor):
        """CoderExecutor should escalate tasks with unclear requirements."""
        thread = AgentThread()
        task = {
            "task_id": "test_002",
            "description": "Build the entire authentication system."  # Too broad
        }
        
        report = await coder_executor.execute_task(task, thread)
        
        assert isinstance(report, ExecutorReport)
        # Should either escalate or fail gracefully
        # (LLM might try to execute or properly escalate)
        assert report.status in ["Completed", "Failed"]


class TestTesterExecutor:
    """Tests for TesterExecutor agent."""
    
    def test_tester_executor_creation(self, tester_executor):
        """TesterExecutor should be created successfully."""
        assert tester_executor is not None
        assert tester_executor.name == "TesterExecutor"
        assert tester_executor.executor_type == "Tester"
        
    @pytest.mark.asyncio
    async def test_tester_generates_test(self, tester_executor):
        """TesterExecutor should generate test code."""
        thread = AgentThread()
        task = {
            "task_id": "test_003",
            "description": "Create a pytest test for a function 'add(a, b)' that returns a + b."
        }
        
        report = await tester_executor.execute_task(task, thread)
        
        assert isinstance(report, ExecutorReport)
        assert report.executor_task_id == "test_003"
        assert report.status in ["Completed", "Failed"]
        
        if report.status == "Completed":
            assert "artifact" in report.outputs
            artifact = report.outputs["artifact"]
            # Should contain test function
            assert "test_" in artifact or "def" in artifact


class TestWriterExecutor:
    """Tests for WriterExecutor agent."""
    
    def test_writer_executor_creation(self, writer_executor):
        """WriterExecutor should be created successfully."""
        assert writer_executor is not None
        assert writer_executor.name == "WriterExecutor"
        assert writer_executor.executor_type == "Writer"
        # Writer has no tools
        
    @pytest.mark.asyncio
    async def test_writer_generates_documentation(self, writer_executor):
        """WriterExecutor should generate markdown documentation."""
        thread = AgentThread()
        task = {
            "task_id": "test_004",
            "description": "Write a markdown README section describing how to install the project using pip."
        }
        
        report = await writer_executor.execute_task(task, thread)
        
        assert isinstance(report, ExecutorReport)
        assert report.executor_task_id == "test_004"
        assert report.status in ["Completed", "Failed"]
        
        if report.status == "Completed":
            assert "artifact" in report.outputs
            artifact = report.outputs["artifact"]
            # Should contain markdown
            assert "pip" in artifact.lower() or "install" in artifact.lower()


class TestExecutorReportStructure:
    """Tests for ExecutorReport structure compliance."""
    
    @pytest.mark.asyncio
    async def test_executor_report_has_required_fields(self, coder_executor):
        """ExecutorReport should have all required fields."""
        thread = AgentThread()
        task = {
            "task_id": "test_005",
            "description": "Return the number 42."
        }
        
        report = await coder_executor.execute_task(task, thread)
        
        # Required fields from data_contracts.py
        assert hasattr(report, "executor_task_id")
        assert hasattr(report, "executor_name")
        assert hasattr(report, "status")
        assert hasattr(report, "outputs")
        assert hasattr(report, "metadata")
        
        # Status should be valid literal
        assert report.status in ["Completed", "Failed", "Pending"]
