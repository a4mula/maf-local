# Phase 10: Multi-Project DevStudio - Implementation Plan

**Phase:** 10.0 (Multi-Project DevStudio)  
**Created:** 2025-11-21  
**Owner:** Dev Lead  
**Estimated Effort:** 3-4 weeks  
**Strategy:** Incremental POC → Full Implementation

---

## Executive Summary

Transform Hierarchical MAF Studio from a single-project system (operating on its own codebase) into a multi-project DevStudio service that can manage external codebases while maintaining strict isolation from its own source code.

**Critical Security Fix:** Eliminates Confused Deputy Problem by making DevStudio source code read-only to agents.

---

## User Review Required

> [!IMPORTANT]
> **Architectural Transformation**
> 
> This phase fundamentally changes how DevStudio operates:
> - **Before:** Agents modify `/home/robb/projects/maf-local` (DevStudio's own code)
> - **After:** Agents work in `/workspaces/{project_id}/` (isolated external projects)
> 
> **Impact:** System source becomes **read-only**. Future DevStudio upgrades must be human-approved Docker rebuilds.

> [!CAUTION]
> **Migration Required**
> 
> Existing PostgreSQL and ChromaDB data must be migrated to include `project_id` scoping.
> Backup recommended before starting Phase 10.

---

## Implementation Strategy: Incremental POC-First

### Rationale

Building full project registry infrastructure before proving isolation patterns is risky. Instead:

1. **Milestone 1:** Hardcoded 2-project POC (DevStudio + test project)
2. **Milestone 2:** Dynamic project registration
3. **Milestone 3:** Session management
4. **Milestone 4:** UI integration

**Benefits:**
- ✅ Validate isolation patterns early
- ✅ Test read-only enforcement before committing
- ✅ Catch design flaws in simple environment
- ✅ Deliver value incrementally

---

## Milestone 1: Foundation & 2-Project POC

**Duration:** 1 week  
**Goal:** Prove isolation with 2 hardcoded projects

### 1.1 Database Schema Updates

#### PostgreSQL: Projects Table

```sql
-- Create projects table
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    workspace_path VARCHAR(512) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',  -- active, archived, deleted
    metadata JSONB DEFAULT '{}'
);

-- Insert DevStudio as Project 0 (special: read-only)
INSERT INTO projects (project_id, name, description, workspace_path, metadata) VALUES
(0, 'maf-local', 'DevStudio itself (read-only)', '/app', '{"read_only": true}'),
(1, 'test-project', 'Test external project', '/workspaces/test-project', '{}');

-- Add project_id to existing tables
ALTER TABLE audit_logs ADD COLUMN project_id INTEGER DEFAULT 0 REFERENCES projects(project_id);
ALTER TABLE governance_decisions ADD COLUMN project_id INTEGER DEFAULT 0 REFERENCES projects(project_id);
ALTER TABLE checkpoints ADD COLUMN project_id INTEGER DEFAULT 0 REFERENCES projects(project_id);

-- Create index for fast filtering
CREATE INDEX idx_audit_logs_project_id ON audit_logs(project_id);
CREATE INDEX idx_governance_project_id ON governance_decisions(project_id);
CREATE INDEX idx_checkpoints_project_id ON checkpoints(project_id);
```

#### PostgreSQL: Sessions Table

```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id INTEGER NOT NULL REFERENCES projects(project_id),
    user_id VARCHAR(255) DEFAULT 'default_user',  -- For future multi-user support
    status VARCHAR(50) DEFAULT 'active',  -- active, paused, completed, failed
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    context JSONB DEFAULT '{}',  -- Session state (current file, branch, etc.)
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_sessions_project_id ON sessions(project_id);
CREATE INDEX idx_sessions_status ON sessions(status);
```

### 1.2 Docker Configuration Updates

#### Update `docker-compose.yaml`

```yaml
services:
  maf-agent:
    volumes:
      # DevStudio source: READ-ONLY
      - ./:/app:ro
      
      # Project workspaces: READ-WRITE
      - ./workspaces/test-project:/workspaces/test-project:rw
      
      # Temporary upgrade proposals (agents can write here)
      - maf-devstudio-upgrades:/tmp/devstudio_upgrades:rw

volumes:
  maf-devstudio-upgrades:
    driver: local
```

### 1.3 Project Context Provider

**File:** `src/persistence/project_context.py`

```python
"""
Project-aware context management.
Ensures all operations are scoped to a project_id.
"""

from typing import Optional
from contextlib import asynccontextmanager


class ProjectContextManager:
    """
    Thread-local storage for current project context.
    All persistence operations must check this.
    """
    
    def __init__(self):
        self._current_project_id: Optional[int] = None
    
    def set_project(self, project_id: int):
        """Set active project for current session."""
        self._current_project_id = project_id
    
    def get_project(self) -> int:
        """Get active project ID."""
        if self._current_project_id is None:
            raise RuntimeError("No active project set. Call set_project() first.")
        return self._current_project_id
    
    def clear_project(self):
        """Clear project context."""
        self._current_project_id = None
    
    @asynccontextmanager
    async def project_scope(self, project_id: int):
        """Context manager for temporary project scope."""
        previous = self._current_project_id
        try:
            self.set_project(project_id)
            yield
        finally:
            if previous is not None:
                self.set_project(previous)
            else:
                self.clear_project()


# Global instance
project_context = ProjectContextManager()
```

### 1.4 Updated ChromaDB Context Provider

**File:** `src/persistence/chromadb_context_provider.py` (update)

```python
async def store(
    self,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store content with automatic project_id scoping."""
    from src.persistence.project_context import project_context
    
    if metadata is None:
        metadata = {}
    
    # Automatically inject project_id
    metadata['project_id'] = project_context.get_project()
    
    doc_id = str(uuid.uuid4())
    self._collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[doc_id]
    )
    return doc_id

async def query(
    self,
    query: str,
    n_results: int = 3,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Query with automatic project_id filtering."""
    from src.persistence.project_context import project_context
    
    if filter_metadata is None:
        filter_metadata = {}
    
    # Force project_id filter
    filter_metadata['project_id'] = project_context.get_project()
    
    results = self._collection.query(
        query_texts=[query],
        n_results=n_results,
        where=filter_metadata
    )
    
    # ... rest of formatting
```

### 1.5 Isolation Tests

**File:** `tests/integration/test_project_isolation.py`

```python
"""
Critical tests for Phase 10: Project isolation enforcement.
"""

import pytest
from src.persistence.project_context import project_context
from src.persistence.chromadb_context_provider import ChromaDBContextProvider


@pytest.mark.asyncio
async def test_chromadb_project_isolation():
    """Verify ChromaDB queries filter by project_id."""
    provider = ChromaDBContextProvider()
    
    # Store in project 0
    async with project_context.project_scope(0):
        doc_id_0 = await provider.store("DevStudio architecture", {"type": "docs"})
    
    # Store in project 1
    async with project_context.project_scope(1):
        doc_id_1 = await provider.store("Test project README", {"type": "docs"})
    
    # Query from project 0 should NOT see project 1 data
    async with project_context.project_scope(0):
        results = await provider.query("README")
        assert len(results) == 0 or all(r['metadata']['project_id'] == 0 for r in results)
    
    # Query from project 1 should see its own data
    async with project_context.project_scope(1):
        results = await provider.query("README")
        assert len(results) > 0
        assert all(r['metadata']['project_id'] == 1 for r in results)


@pytest.mark.asyncio
async def test_read_only_source_enforcement():
    """Verify agents cannot write to /app (DevStudio source)."""
    import os
    
    # Attempt to write to system source
    test_file = "/app/test_write.txt"
    
    with pytest.raises(OSError, match="Read-only file system"):
        with open(test_file, 'w') as f:
            f.write("This should fail")


@pytest.mark.asyncio
async def test_workspace_write_access():
    """Verify agents CAN write to /workspaces/{project_id}/."""
    import os
    
    # Write to project workspace should succeed
    test_file = "/workspaces/test-project/agent_test.txt"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    with open(test_file, 'w') as f:
        f.write("Agents can write here")
    
    assert os.path.exists(test_file)
    
    # Cleanup
    os.remove(test_file)
```

---

## Milestone 2: Dynamic Project Registration

**Duration:** 1 week  
**Goal:** Project CRUD API + dynamic workspace creation

### 2.1 Project Service

**File:** `src/services/project_service.py`

```python
"""
Project management service.
Handles project CRUD, workspace initialization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os


class Project(BaseModel):
    """Project model."""
    project_id: int
    name: str
    description: Optional[str] = None
    workspace_path: str
    status: str = "active"
    metadata: Dict[str, Any] = {}


class ProjectService:
    """Manages project lifecycle."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        git_url: Optional[str] = None
    ) -> Project:
        """
        Create new project with isolated workspace.
        
        Steps:
        1. Insert into projects table
        2. Create /workspaces/{project_id}/ directory
        3. Optionally clone git repo
        4. Initialize ChromaDB collection scope
        """
        workspace_path = f"/workspaces/{name}"
        
        # Insert into DB
        query = """
        INSERT INTO projects (name, description, workspace_path, metadata)
        VALUES ($1, $2, $3, $4)
        RETURNING project_id, name, description, workspace_path, status, metadata
        """
        
        metadata = {"git_url": git_url} if git_url else {}
        
        row = await self.db.fetchrow(
            query,
            name,
            description,
            workspace_path, 
            metadata
        )
        
        # Create workspace directory
        os.makedirs(workspace_path, exist_ok=True)
        
        # Clone git repo if provided
        if git_url:
            import subprocess
            subprocess.run(
                ["git", "clone", git_url, workspace_path],
                check=True
            )
        
        return Project(**row)
    
    async def list_projects(self, status: str = "active") -> List[Project]:
        """List all projects with given status."""
        query = "SELECT * FROM projects WHERE status = $1 ORDER BY created_at DESC"
        rows = await self.db.fetch(query, status)
        return [Project(**row) for row in rows]
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        query = "SELECT * FROM projects WHERE project_id = $1"
        row = await self.db.fetchrow(query, project_id)
        return Project(**row) if row else None
```

### 2.2 FastAPI Project Endpoints

**File:** `src/api/project_api.py`

```python
"""
FastAPI endpoints for project management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.services.project_service import ProjectService, Project
from pydantic import BaseModel


router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    git_url: Optional[str] = None


@router.post("/", response_model=Project)
async def create_project(
    request: CreateProjectRequest,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new project with isolated workspace."""
    try:
        return await service.create_project(
            name=request.name,
            description=request.description,
            git_url=request.git_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Project])
async def list_projects(
    status: str = "active",
    service: ProjectService = Depends(get_project_service)
):
    """List all projects."""
    return await service.list_projects(status=status)


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    """Get project details."""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

---

## Milestone 3: Session Management

**Duration:** 1 week  
**Goal:** Session lifecycle + project switching

### 3.1 Session Service

**File:** `src/services/session_service.py`

```python
"""
Session management for multi-project workflows.
"""

from typing import Optional
from uuid import UUID
import uuid
from pydantic import BaseModel
from datetime import datetime


class Session(BaseModel):
    session_id: UUID
    project_id: int
    user_id: str = "default_user"
    status: str = "active"
    started_at: datetime
    last_activity_at: datetime
    context: dict = {}


class SessionService:
    """Manages session lifecycle."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def start_session(
        self,
        project_id: int,
        user_id: str = "default_user"
    ) -> Session:
        """Start new session for a project."""
        query = """
        INSERT INTO sessions (project_id, user_id, status, context)
        VALUES ($1, $2, 'active', '{}')
        RETURNING session_id, project_id, user_id, status, started_at, last_activity_at, context
        """
        
        row = await self.db.fetchrow(query, project_id, user_id)
        
        # Set project context globally
        from src.persistence.project_context import project_context
        project_context.set_project(project_id)
        
        return Session(**row)
    
    async def switch_session(self, session_id: UUID) -> Session:
        """Switch to existing session (loads project context)."""
        query = """
        UPDATE sessions 
        SET last_activity_at = NOW(), status = 'active'
        WHERE session_id = $1
        RETURNING session_id, project_id, user_id, status, started_at, last_activity_at, context
        """
        
        row = await self.db.fetchrow(query, session_id)
        if not row:
            raise ValueError(f"Session {session_id} not found")
        
        session = Session(**row)
        
        # Update project context
        from src.persistence.project_context import project_context
        project_context.set_project(session.project_id)
        
        return session
```

---

## Milestone 4: UI Integration

**Duration:** 1 week  
**Goal:** Project selector in Streamlit + Next.js

### 4.1 Streamlit Updates

**File:** `src/ui/streamlit_app.py` (update)

```python
import streamlit as st
import requests

# Project selector
def render_project_selector():
    """Render project selector dropdown."""
    response = requests.get("http://localhost:8002/api/projects/")
    projects = response.json()
    
    project_options = {p['name']: p['project_id'] for p in projects}
    
    selected_name = st.selectbox(
        "Select Project",
        options=list(project_options.keys())
    )
    
    selected_id = project_options[selected_name]
    
    # Store in session state
    if st.session_state.get('current_project_id') != selected_id:
        # Switch session
        response = requests.post(
            "http://localhost:8002/api/sessions/start",
            json={"project_id": selected_id}
        )
        st.session_state['current_project_id'] = selected_id
        st.session_state['session_id'] = response.json()['session_id']
    
    return selected_id

# Main app
def main():
    st.title("🤖 MAF DevStudio")
    
    # Project selector at top
    project_id = render_project_selector()
    
    st.write(f"**Active Project:** {project_id}")
    
    # Rest of chat UI...
```

---

## Verification Plan

### Automated Tests

```bash
# Unit tests
pytest tests/unit/test_project_service.py -v
pytest tests/unit/test_session_service.py -v

# Integration tests (CRITICAL)
pytest tests/integration/test_project_isolation.py -v
pytest tests/integration/test_read_only_enforcement.py -v
pytest tests/integration/test_session_switching.py -v

# End-to-end
pytest tests/e2e/test_multi_project_workflow.py -v
```

### Manual Verification

1. **Create 2 projects via API:**
   ```bash
   curl -X POST http://localhost:8002/api/projects/ \
     -H "Content-Type: application/json" \
     -d '{"name": "test-project-1", "description": "First test project"}'
   ```

2. **Verify isolation:**
   - Add document to project 1
   - Switch to project 2
   - Query ChromaDB
   - Verify project 1 data NOT visible

3. **Test read-only enforcement:**
   - Start session for project 0 (DevStudio)
   - Ask agent to "delete src/agents/liaison_agent.py"
   - Verify error: "Read-only file system"

---

## Migration Checklist

- [ ] **Backup Current State**
  - [ ] Export PostgreSQL: `pg_dump maf_db > backup.sql`
  - [ ] Export ChromaDB: `docker exec maf-chroma tar -czf /tmp/chroma.tar.gz /chroma/data`

- [ ] **Run Migrations**
  - [ ] Create `projects` table
  - [ ] Create `sessions` table
  - [ ] Add `project_id` columns to existing tables
  - [ ] Insert Project 0 (maf-local)

- [ ] **Update Docker Compose**
  - [ ] Add read-only mount for `/app`
  - [ ] Create workspace volumes

- [ ] **Test in Isolation**
  - [ ] Run `test_project_isolation.py`
  - [ ] Run `test_read_only_enforcement.py`
  - [ ] Manual smoke test

- [ ] **Document Rollback**
  - [ ] Keep backup for 1 week
  - [ ] Document restore procedure

---

## Success Criteria

- [x] MAF SDK compliance (Phase 10.1 complete)
- [ ] DevStudio source code read-only (verified by test)
- [ ] ≥2 projects managed simultaneously
- [ ] Zero context bleed between projects (verified by test)
- [ ] Session persistence across restarts
- [ ] UI supports project selection

---

## Rollback Plan

If critical issues arise:

1. **Restore Database:**
   ```bash
   psql maf_db < backup.sql
   ```

2. **Revert Docker Compose:**
   - Remove `:ro` from source mount
   - Remove workspace volumes

3. **Verify System:**
   - Test basic chat workflow
   - Check data integrity

**Estimated Rollback Time:** 30 minutes

---

## Post-Implementation

### Documentation Updates

Per MANIFEST.yaml:

1. **architecture/CURRENT.md:**
   - Add Project Registry architecture
   - Update persistence layer diagram

2. **feedback/CURRENT.md:**
   - Mark PoLA violation as RESOLVED

3. **planning/ARCHIVE.md:**
   - Add Phase 10 summary

### Next Phase Prerequisites

Phase 10 unblocks:
- **Phase 11:** Documentation automation (can now scope by project)
- **Phase 12:** Multi-tenancy (project → user mapping)
- **Phase 13:** Cloud deployment (Azure Container Instances)

---

## Quick Links

- **Current Phase:** [CURRENT.md](../CURRENT.md)
- **Architecture:** [architecture/CURRENT.md](../../architecture/CURRENT.md)
- **Rationale:** [why/RATIONALE.md](../../why/RATIONALE.md#why-read-only-source-mount-phase-10)
