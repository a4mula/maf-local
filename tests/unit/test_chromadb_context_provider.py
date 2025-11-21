"""
Unit tests for ChromaDBContextProvider.

Tests the MAF SDK-compliant Context Provider implementation.
"""

import pytest
import asyncio
from src.persistence.chromadb_context_provider import ChromaDBContextProvider


@pytest.fixture
def provider():
    """Create a test Context Provider instance."""
    return ChromaDBContextProvider(
        host="localhost",
        port=8000,
        collection_name="test_maf_knowledge"
    )


@pytest.mark.asyncio
async def test_store_and_retrieve(provider):
    """Test basic storage and retrieval."""
    # Store a document
    content = "MAF SDK compliance is critical for enterprise deployment"
    metadata = {"topic": "compliance", "priority": "high"}
    
    doc_id = await provider.store(content, metadata)
    
    assert doc_id is not None
    assert isinstance(doc_id, str)
    
    # Retrieve the document
    retrieved = await provider.retrieve(doc_id)
    
    assert retrieved is not None
    assert retrieved["content"] == content
    assert retrieved["metadata"]["topic"] == "compliance"


@pytest.mark.asyncio
async def test_query_with_metadata(provider):
    """Test querying with metadata filtering."""
    # Store multiple documents
    await provider.store(
        "Phase 10.1 focuses on MAF SDK compliance",
        {"phase": "10.1", "topic": "compliance"}
    )
    await provider.store(
        "Phase 10 is about multi-project support",
        {"phase": "10", "topic": "features"}
    )
    
    # Query all documents
    all_results = await provider.query("MAF SDK", n_results=10)
    assert len(all_results) >= 1
    
    # Query with metadata filter
    filtered_results = await provider.query(
        "MAF",
        n_results=10,
        filter_metadata={"phase": "10.1"}
    )
    
    assert len(filtered_results) >= 1
    for result in filtered_results:
        assert result["metadata"]["phase"] == "10.1"


@pytest.mark.asyncio
async def test_delete_document(provider):
    """Test document deletion."""
    # Store a document
    doc_id = await provider.store("Test document for deletion", {})
    
    # Verify it exists
    retrieved = await provider.retrieve(doc_id)
    assert retrieved is not None
    
    # Delete it
    success = await provider.delete(doc_id)
    assert success is True
    
    # Verify it's gone
    retrieved_after = await provider.retrieve(doc_id)
    assert retrieved_after is None


@pytest.mark.asyncio
async def test_async_operations(provider):
    """Test that all operations are truly async."""
    # Store multiple documents concurrently
    tasks = [
        provider.store(f"Document {i}", {"index": i})
        for i in range(5)
    ]
    
    doc_ids = await asyncio.gather(*tasks)
    
    assert len(doc_ids) == 5
    assert all(isinstance(doc_id, str) for doc_id in doc_ids)


def test_is_connected_property(provider):
    """Test the is_connected property."""
    # If ChromaDB is running, should be connected
    # This test may fail if ChromaDB is not running, which is expected
    assert isinstance(provider.is_connected, bool)


@pytest.mark.asyncio
async def test_error_handling_when_disconnected():
    """Test graceful error handling when ChromaDB is unavailable."""
    # Create provider with invalid host
    provider = ChromaDBContextProvider(
        host="invalid-host",
        port=9999,
        collection_name="test"
    )
    
    # Should raise RuntimeError when trying to store
    with pytest.raises(RuntimeError, match="ChromaDB collection not available"):
        await provider.store("test content", {})
