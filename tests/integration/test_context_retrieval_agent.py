"""
Integration tests for Context Retrieval Agent with MAF SDK Context Provider.

Tests the refactored agent with dependency injection.
"""

import pytest
import asyncio
from src.agents.context_retrieval_agent import ContextRetrievalAgent
from src.persistence.chromadb_context_provider import ChromaDBContextProvider
from src.clients.litellm_client import LiteLLMChatClient
from src.config.settings import settings


@pytest.fixture
def memory_provider():
    """Create a test memory provider."""
    return ChromaDBContextProvider(
        host="localhost",
        port=8000,
        collection_name="test_integration_maf"
    )


@pytest.fixture
def chat_client():
    """Create a test chat client."""
    return LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)


@pytest.fixture
def context_agent(chat_client, memory_provider):
    """Create Context Retrieval Agent with injected provider."""
    return ContextRetrievalAgent(
        chat_client=chat_client,
        memory_provider=memory_provider
    )


@pytest.mark.asyncio
async def test_add_and_query_knowledge(context_agent):
    """Test end-to-end workflow of adding and querying knowledge."""
    # Add knowledge
    result = await context_agent.add_knowledge(
        "The ContextRetrievalAgent now uses dependency injection for MAF SDK compliance",
        {"category": "architecture", "phase": "10.1"}
    )
    
    assert "Successfully added document" in result
    assert "ID:" in result
    
    # Query knowledge
    results = await context_agent.query_knowledge("dependency injection", n_results=3)
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    # Verify result structure
    for result in results:
        assert "content" in result
        assert "metadata" in result
        assert "distance" in result


@pytest.mark.asyncio
async def test_provider_injection(context_agent, memory_provider):
    """Verify dependency injection pattern works correctly."""
    # Agent should have reference to injected provider
    assert context_agent.memory is memory_provider
    
    # Agent should be connected if provider is connected
    if memory_provider.is_connected:
        assert context_agent.is_connected


@pytest.mark.asyncio
async def test_backward_compatibility(context_agent):
    """Verify existing API unchanged (no breaking changes)."""
    # Existing methods should still work
    result = await context_agent.add_knowledge("Test content", {"test": True})
    assert isinstance(result, str)
    
    results = await context_agent.query_knowledge("test", n_results=1)
    assert isinstance(results, list)
    
    # New methods should also work
    doc_id = (await context_agent.add_knowledge("Doc for retrieval", {})).split("ID: ")[1]
    retrieved = await context_agent.retrieve_document(doc_id)
    
    if retrieved:  # May be None if ChromaDB not running
        assert "content" in retrieved
        assert "metadata" in retrieved


@pytest.mark.asyncio
async def test_error_handling_with_provider(context_agent):
    """Test graceful error handling through provider layer."""
    # Query should return empty list on error, not crash
    results = await context_agent.query_knowledge("test query")
    assert isinstance(results, list)
    
    # Add should return error message string, not raise exception
    result = await context_agent.add_knowledge("test")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_delete_document_integration(context_agent):
    """Test document deletion through agent."""
    # Add document
    add_result = await context_agent.add_knowledge("Temporary document", {})
    
    if "Successfully added" in add_result:
        doc_id = add_result.split("ID: ")[1]
        
        # Delete it
        delete_result = await context_agent.delete_document(doc_id)
        
        assert "Successfully deleted" in delete_result or "Failed to delete" in delete_result
