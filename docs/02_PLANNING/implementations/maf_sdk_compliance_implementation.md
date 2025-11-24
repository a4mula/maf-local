# MAF SDK Compliance Implementation Plan

**Phase:** 10.1 (MAF SDK Compliance Refactoring)  
**Created:** 2025-11-21  
**Owner:** Dev Lead  
**Estimated Effort:** 4-6 hours

---

## Goal

Refactor memory persistence layer to comply with Microsoft Agent Framework (MAF SDK) standards by implementing the `Context Providers` interface for ChromaDB access.

## User Review Required

> [!IMPORTANT]
> **Architectural Change**
> 
> This refactoring changes how `ContextRetrievalAgent` accesses persistent memory:
> - **Before**: Direct `chromadb.HttpClient` instantiation (non-compliant)
> - **After**: MAF SDK `ContextProvider` interface with dependency injection (compliant)
> 
> **Impact**: Improves portability, enables enterprise governance, and unblocks Phase 10.

---

## Proposed Changes

### 1. Memory Persistence Layer

#### [NEW] [`src/persistence/chromadb_context_provider.py`](file:///home/robb/projects/maf-local/src/persistence/chromadb_context_provider.py)

**Purpose:** Implement MAF SDK `ContextProvider` interface for ChromaDB.

**Implementation:**

```python
from typing import List, Dict, Any, Optional
import chromadb
from microsoft_agents.storage import ContextProvider  # MAF SDK interface


class ChromaDBContextProvider(ContextProvider):
    """
    MAF SDK-compliant Context Provider for ChromaDB.
    Implements the ContextProvider interface for persistent agent memory.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "maf_knowledge"
    ):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection_name = collection_name
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists."""
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
    
    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store content in ChromaDB.
        
        Args:
            content: Document content to store
            metadata: Optional metadata dict
        
        Returns:
            Document ID
        """
        import uuid
        doc_id = str(uuid.uuid4())
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        
        return doc_id
    
    async def query(
        self,
        query: str,
        n_results: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query ChromaDB for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of matching documents with metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results to MAF SDK standard
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results
    
    async def retrieve(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific document by ID.
        
        Args:
            document_id: Document identifier
        
        Returns:
            Document dict or None if not found
        """
        try:
            result = self.collection.get(ids=[document_id])
            if result['documents']:
                return {
                    "content": result['documents'][0],
                    "metadata": result['metadatas'][0] if result['metadatas'] else {}
                }
        except Exception:
            return None
    
    async def delete(self, document_id: str) -> bool:
        """
        Delete document by ID.
        
        Args:
            document_id: Document identifier
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            return True
        except Exception:
            return False
```

**Rationale:**
- Implements MAF SDK `ContextProvider` interface
- Maintains existing ChromaDB functionality
- Adds proper async/await and type hints
- Enables dependency injection

---

#### [MODIFY] [`src/agents/context_retrieval_agent.py`](file:///home/robb/projects/maf-local/src/agents/context_retrieval_agent.py)

**Changes:**

```python
# BEFORE (Lines 1-30) - Direct ChromaDB access ❌
import chromadb
from chromadb.config import Settings

class ContextRetrievalAgent:
    def __init__(self, chat_client: IChatClient):
        self.chroma_client = chromadb.HttpClient(
            host="localhost",
            port=8000
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="maf_knowledge"
        )

# AFTER - MAF SDK Context Provider ✅
from typing import Dict, Any, List, Optional
from src.clients.base import IChatClient
from src.persistence.chromadb_context_provider import ChromaDBContextProvider

class ContextRetrievalAgent:
    """
    Tier 3 Agent: Context Retrieval Agent (The Librarian)
    Responsible for storing and retrieving knowledge via MAF SDK Context Provider.
    """
    
    def __init__(
        self,
        chat_client: IChatClient,
        memory_provider: ChromaDBContextProvider  # Dependency injection
    ):
        self.name = "ContextRetrievalAgent"
        self.chat_client = chat_client
        self.memory = memory_provider  # Use provider interface
    
    async def add_knowledge(
        self,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a document to the knowledge base."""
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
        """Query the knowledge base for relevant documents."""
        try:
            return await self.memory.query(query, n_results)
        except Exception as e:
            print(f"[ContextRetrievalAgent] Error querying knowledge: {e}")
            return []
    
    # ... rest of the methods use self.memory instead of self.collection
```

**Key Changes:**
- ✅ Accept `ChromaDBContextProvider` in constructor
- ✅ Remove direct `chromadb.HttpClient` instantiation
- ✅ Use `self.memory` provider interface for all operations
- ✅ Maintains existing public API (no breaking changes)

---

#### [MODIFY] [`src/services/agent_factory.py`](file:///home/robb/projects/maf-local/src/services/agent_factory.py)

**Changes:**

```python
from src.persistence.chromadb_context_provider import ChromaDBContextProvider
from src.agents.context_retrieval_agent import ContextRetrievalAgent

def create_context_retrieval_agent(chat_client):
    """Factory method for Context Retrieval Agent."""
    
    # Create MAF SDK-compliant memory provider
    memory_provider = ChromaDBContextProvider(
        host="localhost",  # In Docker: "maf-chroma"
        port=8000,
        collection_name="maf_knowledge"
    )
    
    # Inject provider into agent
    return ContextRetrievalAgent(
        chat_client=chat_client,
        memory_provider=memory_provider
    )
```

**Rationale:**
- Centralized provider instantiation
- Enables environment-specific configuration
- Simplifies testing (mock provider injection)

---

## Verification Plan

### Automated Tests

**1. Context Provider Unit Tests**

```bash
# File: tests/unit/test_chromadb_context_provider.py
pytest tests/unit/test_chromadb_context_provider.py -v
```

**Test cases:**
- `test_store_and_retrieve()` - Basic storage/retrieval
- `test_query_with_metadata()` - Metadata filtering
- `test_delete_document()` - Deletion operations
- `test_async_operations()` - Async/await compliance

**2. Context Retrieval Agent Integration Tests**

```bash
# File: tests/integration/test_context_retrieval_agent.py
pytest tests/integration/test_context_retrieval_agent.py -v
```

**Test cases:**
- `test_add_and_query_knowledge()` - End-to-end workflow
- `test_provider_injection()` - DI pattern verification
- `test_backward_compatibility()` - Existing API unchanged

### Manual Verification

1. **Start Stack**: `./scripts/start_node.sh`
2. **Access Streamlit**: http://localhost:8501
3. **Test Commands**:
   - `store: MAF SDK compliance is critical`
   - `query: MAF SDK`
   - Verify storage and retrieval work correctly

---

## Migration Path

**No data migration required** - ChromaDB data persists across refactoring.

1. **Backup** (optional but recommended):
   ```bash
   docker exec maf-chroma tar -czf /tmp/chroma_backup.tar.gz /chroma/data
   ```

2. **Apply Code Changes**: Implement all file modifications above

3. **Restart Services**:
   ```bash
   docker compose down
   docker compose up -d
   ```

4. **Verify Health**: Check ChromaDB accessible via provider

---

## Rollback Plan

If issues occur:

1. **Revert Code**: `git revert <commit>`
2. **Restart**: `docker compose restart maf-agent`
3. **Verify**: Existing direct ChromaDB access restored

**Risk**: Low (no database schema changes)

---

## Success Metrics

- [ ] All unit tests pass (100% coverage for provider)
- [ ] All integration tests pass
- [ ] Zero direct `chromadb` imports in agent code
- [ ] ChromaDB operations function identically
- [ ] MAF SDK compliance audit resolves violation

---

## Post-Implementation

### Documentation Updates

1. Update [`CURRENT_STATE.md`](../architecture/CURRENT_STATE.md):
   - Document new `ChromaDBContextProvider` architecture
   - Update agent dependency diagram

2. Update [`maf_sdk_compliance_audit.md`](../feedback/maf_sdk_compliance_audit.md):
   - Mark Section 3 (Memory Persistence) as ✅ RESOLVED

3. Update [`CURRENT_PHASE.md`](./CURRENT_PHASE.md):
   - Mark all tasks complete
   - Prepare for Phase 10

### Phase Archive

Summarize this sub-phase in [`Phase_Planner_ARCHIVE.md`](./Phase_Planner_ARCHIVE.md):

```markdown
## **Phase 10.1: MAF SDK Compliance** ✅ COMPLETED

**Duration:** 6 hours (November 21, 2025)  
**Goal:** Refactor memory layer for MAF SDK compliance

### Key Deliverable
- Implemented `ChromaDBContextProvider` with MAF SDK `ContextProvider` interface
- Refactored `ContextRetrievalAgent` to use dependency injection
- Achieved 100% MAF SDK compliance (up from 70%)

**Outcome:** Ready for Phase 10 multi-project implementation.
```

---

## Quick Links

- **Audit Report**: [MAF SDK Compliance Audit](../feedback/maf_sdk_compliance_audit.md)
- **Standards**: [MAF SDK Reference](../research/maf_sdk_standards.md)
- **Current Phase**: [CURRENT_PHASE.md](./CURRENT_PHASE.md)
