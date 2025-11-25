import pytest
from unittest.mock import MagicMock, AsyncMock
from src.agents.domain_leads.qa_domain_lead import QADomainLead
from src.models.data_contracts import TaskDefinition

@pytest.mark.asyncio
async def test_qa_domain_lead_initialization():
    """Test that QADomainLead initializes with correct domain and instructions."""
    mock_client = MagicMock()
    mock_tlb = MagicMock()
    
    qa_lead = QADomainLead(mock_client, mock_tlb)
    
    assert qa_lead.domain == "QA"
    assert qa_lead.tlb_workflow == mock_tlb

@pytest.mark.asyncio
async def test_qa_domain_lead_task_breakdown_fallback():
    """Test that QADomainLead falls back to generic subtask if LLM fails."""
    mock_client = MagicMock()
    mock_tlb = MagicMock()
    
    # Mock run to raise exception (simulating parsing failure or LLM error)
    mock_client.run = AsyncMock(side_effect=Exception("LLM Error"))
    
    qa_lead = QADomainLead(mock_client, mock_tlb)
    # Mock the internal run method (since ChatAgent wraps the client)
    qa_lead.run = AsyncMock(side_effect=Exception("LLM Error"))
    
    task_def = TaskDefinition(
        task_id="task_123",
        description="Verify login flow",
        domain="QA",
        priority="High"
    )
    
    # We need to mock _break_down_task directly or test execute_task which calls it
    # But _break_down_task calls self.run. 
    # Let's test _break_down_task directly with the mocked run.
    
    subtasks = await qa_lead._break_down_task(task_def, MagicMock())
    
    assert len(subtasks) == 1
    assert subtasks[0]["executor_type"] == "coder" # Base falls back to coder
    assert "Verify login flow" in subtasks[0]["description"]
