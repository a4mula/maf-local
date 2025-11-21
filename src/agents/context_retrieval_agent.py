"""
Context Retrieval Agent - MAF SDK Compliant Implementation

Tier 3 Agent responsible for storing and retrieving knowledge using
MAF SDK Context Provider pattern (dependency injection).
"""

from typing import List, Dict, Any, Optional
from src.clients.base import IChatClient
from src.persistence.chromadb_context_provider import ChromaDBContextProvider


class ContextRetrievalAgent:
    """
    Tier 3 Agent: Context Retrieval Agent (The Librarian)
    
    Responsible for storing and retrieving knowledge via MAF SDK-compliant
    Context Provider interface. Uses dependency injection for testability
    and enterprise governance integration.
    """
    
    def __init__(
        self,
        chat_client: IChatClient,
        memory_provider: ChromaDBContextProvider
    ):
        """
        Initialize Context Retrieval Agent.
        
        Args:
            chat_client: LLM client for conversational interactions
            memory_provider: MAF SDK Context Provider for persistent memory
        """
        self.name = "ContextRetrievalAgent"
        self.chat_client = chat_client
        self.memory = memory_provider  # Use provider interface
    
    async def add_knowledge(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            content: Document content to store
            metadata: Optional metadata dict
        
        Returns:
            Success/error message with document ID
        """
        try:
            doc_id = await self.memory.store(content, metadata)
            return f"Successfully added document with ID: {doc_id}"
        except Exception as e:
            return f"Error adding document: {e}"
    
    async def query_knowledge(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant documents.
        
        Args:
            query: Search query string
            n_results: Number of results to return (default: 3)
        
        Returns:
            List of matching documents with metadata and distance scores
        """
        try:
            return await self.memory.query(query, n_results)
        except Exception as e:
            print(f"[ContextRetrievalAgent] Error querying knowledge: {e}")
            return []
    
    async def retrieve_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: Document identifier
        
        Returns:
            Document dict or None if not found
        """
        try:
            return await self.memory.retrieve(document_id)
        except Exception as e:
            print(f"[ContextRetrievalAgent] Error retrieving document: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> str:
        """
        Delete a document from the knowledge base.
        
        Args:
            document_id: Document identifier
        
        Returns:
            Success/error message
        """
        try:
            success = await self.memory.delete(document_id)
            if success:
                return f"Successfully deleted document {document_id}"
            else:
                return f"Failed to delete document {document_id}"
        except Exception as e:
            return f"Error deleting document: {e}"
    
    @property
    def is_connected(self) -> bool:
        """Check if memory provider is connected and available."""
        return self.memory.is_connected
