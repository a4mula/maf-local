"""
Unit Tests for ResearchExecutor
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agent_framework import AgentThread
from src.agents.executors.research_executor import ResearchExecutor
from src.models.data_contracts import ExecutorReport

@pytest.fixture
def chat_client():
    """Mock chat client."""
    client = MagicMock()
    # Mock the run method response
    mock_response = MagicMock()
    mock_response.text = "Research findings"
    client.run = AsyncMock(return_value=mock_response)
    return client

@pytest.fixture
def research_executor(chat_client):
    """Create ResearchExecutor instance."""
    return ResearchExecutor(chat_client=chat_client)

class TestResearchExecutor:
    
    @pytest.mark.asyncio
    async def test_execute_task_new(self, research_executor):
        """Should execute new task and cache result."""
        thread = AgentThread()
        task = {
            "task_id": "task_1",
            "description": "Research Python caching"
        }
        
        # Mock the super().run() call which is called by execute_task
        # Since we can't easily mock super(), we rely on the mocked chat_client
        # injected into the instance.
        
        # Mock the run method of the executor itself to simulate LLM response
        research_executor.run = AsyncMock(return_value=MagicMock(text="Python caching is useful"))
        
        report = await research_executor.execute_task(task, thread)
        
        assert report.status == "Completed"
        assert report.outputs["artifact"] == "Python caching is useful"
        assert "cached" not in report.metadata
        
        # Verify it's in cache
        assert "Research Python caching" in research_executor._cache
        assert research_executor._cache["Research Python caching"] == "Python caching is useful"

    @pytest.mark.asyncio
    async def test_execute_task_cached(self, research_executor):
        """Should return cached result for repeated task."""
        thread = AgentThread()
        task = {
            "task_id": "task_2",
            "description": "Research caching"
        }
        
        # Pre-populate cache
        research_executor._cache["Research caching"] = "Cached result"
        
        # Execute (should not call LLM)
        research_executor.run = AsyncMock()
        
        report = await research_executor.execute_task(task, thread)
        
        assert report.status == "Completed"
        assert report.outputs["artifact"] == "Cached result"
        assert report.metadata.get("cached") is True
        
        # Verify run was NOT called
        research_executor.run.assert_not_called()

    def test_clear_cache(self, research_executor):
        """Should clear the cache."""
        research_executor._cache["key"] = "value"
        research_executor.clear_cache()
        assert len(research_executor._cache) == 0
