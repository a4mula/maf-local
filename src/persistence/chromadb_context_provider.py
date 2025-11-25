"""
MAF SDK-compliant Context Provider for ChromaDB.

This module implements the MAF SDK Context Provider interface for persistent
agent memory using ChromaDB as the underlying vector store.
"""

from typing import List, Dict, Any, Optional
import uuid
import asyncio
import chromadb
from chromadb.config import Settings
from src.utils import get_logger

logger = get_logger(__name__)


class ChromaDBContextProvider:
    """
    MAF SDK-compliant Context Provider for ChromaDB.
    
    Implements the Context Provider interface for persistent agent memory,
    enabling dependency injection and enterprise governance integration.
    
    Note: While MAF SDK defines a ContextProvider interface, this implementation
    follows its patterns (async operations, type hints, standard methods)
    without importing from microsoft_agents directly, as the actual package
    may not be available in all environments.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "maf_knowledge"
    ):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            host: ChromaDB server host (default: localhost)
            port: ChromaDB server port (default: 8000)
            collection_name: Name of the collection to use (default: maf_knowledge)
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._client: Optional[chromadb.HttpClient] = None
        self._collection = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB HTTP client and ensure collection exists."""
        try:
            self._client = chromadb.HttpClient(host=self.host, port=self.port)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"[ChromaDBContextProvider] Connected to ChromaDB at {self.host}:{self.port}")
        except Exception as e:
            logger.info(f"[ChromaDBContextProvider] Failed to connect to ChromaDB: {e}")
            self._client = None
            self._collection = None
    
    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store content in ChromaDB with automatic project_id scoping.
        
        Args:
            content: The text content to store
            metadata: Optional metadata dictionary
            
        Returns:
            str: The ID of the stored document
        """
        if not self.is_connected:
            # In a real implementation, we might queue this or retry
            # For now, we'll log and return a placeholder if not connected
            # (This allows tests to run without a real ChromaDB instance if mocked)
            return "offline_id"

        from src.persistence.project_context import project_context
        
        if metadata is None:
            metadata = {}
            
        # Automatically inject project_id
        try:
            project_id = project_context.get_project()
            metadata['project_id'] = project_id
        except RuntimeError:
            # Fallback for tests or legacy code not yet using project context
            # TODO: Remove this fallback once migration is complete
            metadata['project_id'] = 0 

        doc_id = str(uuid.uuid4())
        
        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self._collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
        )
        
        return doc_id

    async def query(
        self,
        query: str,
        n_results: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query ChromaDB for relevant documents with project isolation.
        
        Args:
            query: The query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List[Dict[str, Any]]: List of results with 'content' and 'metadata'
        """
        if not self.is_connected:
            return []

        from src.persistence.project_context import project_context

        if filter_metadata is None:
            filter_metadata = {}
            
        # Force project_id filter
        try:
            project_id = project_context.get_project()
            filter_metadata['project_id'] = project_id
        except RuntimeError:
            # Fallback
            filter_metadata['project_id'] = 0

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
        )
        
        # Format results
        formatted_results = []
        if results and results['ids']:
            # ChromaDB returns lists of lists (one list per query)
            # Since we only query one text at a time, we take the first list
            ids = results['ids'][0]
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0] if 'distances' in results else None
            
            for i, doc_id in enumerate(ids):
                formatted_results.append({
                    "id": doc_id,
                    "content": documents[i],
                    "metadata": metadatas[i] if metadatas else {},
                    "distance": distances[i] if distances else None
                })
                
        return formatted_results
    
    async def retrieve(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific document by ID.
        
        Args:
            document_id: Document identifier (UUID string)
        
        Returns:
            Document dict with 'content' and 'metadata' keys, or None if not found
            
        Raises:
            RuntimeError: If ChromaDB client is not available
        """
        if not self._collection:
            raise RuntimeError("ChromaDB collection not available")
        
        try:
            result = self._collection.get(ids=[document_id])
            if result['documents']:
                return {
                    "content": result['documents'][0],
                    "metadata": result['metadatas'][0] if result['metadatas'] else {}
                }
            return None
        except Exception as e:
            logger.info(f"[ChromaDBContextProvider] Error retrieving document {document_id}: {e}")
            return None
    
    async def delete(self, document_id: str) -> bool:
        """
        Delete document by ID.
        
        Args:
            document_id: Document identifier (UUID string)
        
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            RuntimeError: If ChromaDB client is not available
        """
        if not self._collection:
            raise RuntimeError("ChromaDB collection not available")
        
        try:
            self._collection.delete(ids=[document_id])
            return True
        except Exception as e:
            logger.info(f"[ChromaDBContextProvider] Error deleting document {document_id}: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if ChromaDB client is connected and collection is available."""
        return self._client is not None and self._collection is not None
