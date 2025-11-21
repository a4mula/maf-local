---
access: read-write
audience: agents
update_trigger: standards_change | pattern_added
managed_by: Human approval required for MAF SDK standards
---

# MAF Local: Agent Guidelines

**For:** All agents working on this project  
**Last Updated:** 2025-11-21

> [!IMPORTANT]
> This document defines **mandatory** coding standards, architectural patterns, and agent behaviors for the MAF Local project.

---

## Quick Reference

| Need | See Section |
|:---|:---|
| Project config (stack, ports, hardware) | [Project Configuration](#project-configuration) |
| Python/JS code style | [Code Style](#code-style) |
| MAF SDK requirements (async, types, providers) | [MAF SDK Standards](#maf-sdk-mandatory-coding-standards) |
| Common code patterns | [Common Patterns](#common-patterns) |
| Development commands | [Tools & Workflows](#tools-and-workflows) |
| File organization | [File Organization](#file-organization) |
| Security rules | [Security Guidelines](#security-guidelines) |
| Documentation updates | [Documentation System](#documentation-system-usage) |

---

## Project Configuration

**Project Name:** MAF Local (Hierarchical DevStudio)  
**Primary Language:** Python 3.10+  
**Framework:** Microsoft Agent Framework (MAF SDK), Docker, FastAPI, Streamlit, Next.js  
**Local LLM:** Ollama (Llama 3.1 8B Instruct)  
**Cloud Fallback:** Gemini 2.0 Flash (via LiteLLM)  
**Database:** PostgreSQL (governance, checkpoints), ChromaDB (vector memory)  
**GPU Requirement:** NVIDIA with CUDA (8GB+ VRAM)

---

## Code Style

### Python (Primary)

- **PEP 8 compliant** with line length of 100 characters
- Use `black` for formatting
- **Type hints REQUIRED** for all function signatures (see [MAF SDK Standards](#maf-sdk-mandatory-coding-standards))
- **Async/await for ALL I/O** operations (see [MAF SDK Standards](#maf-sdk-mandatory-coding-standards))

**Example:**
```python
async def process_message(
    message: str,
    session_id: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Process user message and return response."""
    response = await llm_client.chat(message)
    await database.save(response)
    return {"response": response}
```

### JavaScript/TypeScript (ui-next)

- **ESLint + Prettier** for formatting
- TypeScript for all new code
- React functional components with hooks
- TailwindCSS for styling (no inline styles)

---

## Architecture Principles

### 1. Hierarchical Agent System

**4 Tiers**: Liaison → Project Lead → Domain Leads → Executors

- **Separation of Concerns**: Each tier has specific responsibilities
- **Escalation**: Agents escalate uncertainty upward, never make assumptions

### 2. Principle of Least Authority (PoLA)

- Agents only have access to tools they need
- Read-only access to DevStudio source code (Phase 10+)
- All file operations audited via ArtifactManager

### 3. FOSS-First Philosophy

- Prioritize local models (Ollama) over cloud
- Fall back to Gemini only when local models insufficient
- Track and minimize cloud API costs

### 4. Observability

- All agent actions logged to PostgreSQL
- Metrics exposed to Prometheus
- Checkpoints for resumable workflows

---

## MAF SDK Mandatory Coding Standards

> [!IMPORTANT]
> The following standards are **REQUIRED** for Microsoft Agent Framework (MAF SDK) compliance.  
> See [MAF SDK Standards](../research/maf_sdk_standards.md) and [Compliance Audit](../feedback/maf_sdk_compliance_audit.md) for details.

### 1. Asynchronous Development (REQUIRED)

All I/O operations MUST use Python's `asyncio` framework for non-blocking execution.

```python
# ✅ Correct - Non-blocking I/O
async def process_message(message: str) -> str:
    response = await llm_client.chat(message)
    result = await database.save(response)
    return response

# ❌ Wrong - Blocking I/O (blocks event loop!)
def process_message(message: str) -> str:
    response = llm_client.chat(message)  # Blocks!
    return response
```

**Rationale**: Agent execution invariably involves network I/O (LLM calls, database operations). Async I/O ensures high throughput and prevents blocking.

**When to use `async`**:
- LLM API calls
- Database queries (PostgreSQL, ChromaDB)
- HTTP requests
- File I/O (when using `aiofiles`)
- Any tool execution involving I/O

### 2. Type Hints (REQUIRED)

Python type hints are **MANDATORY** on all function signatures.

```python
from typing import Dict, List, Optional, Any

# ✅ Correct - Complete type hints
async def calculate_risk(
    transaction_amount: float,
    user_history: Dict[str, Any],
    threshold: Optional[float] = 0.5
) -> Dict[str, float]:
    risk_score = analyze(transaction_amount, user_history)
    return {"risk": risk_score, "threshold": threshold}

# ❌ Wrong - No type hints
async def calculate_risk(transaction_amount, user_history, threshold=0.5):
    risk_score = analyze(transaction_amount, user_history)
    return {"risk": risk_score, "threshold": threshold}
```

**Rationale**: Required for MAF SDK features:
- `AIFunction` auto-generates JSON schemas from type hints for LLM tool calling
- Workflow engine enforces type-safe message passing
- Enterprise tooling requires schema validation
- Improves IDE autocomplete and catches errors early

**Type Hint Standards**:
- Use `typing` module for complex types (`Dict`, `List`, `Optional`, `Union`)
- Use `Any` sparingly - prefer specific types
- Always specify return types (use `-> None` for procedures)
- Use `Optional[T]` for nullable parameters

### 3. Context Providers for Memory (REQUIRED)

Persistent agent memory MUST use MAF SDK's `Context Providers` interface. **Direct database access violates MAF SDK architecture.**

```python
# ✅ Correct - Uses Context Provider interface
from src.persistence.chromadb_context_provider import ChromaDBContextProvider

class MyAgent:
    def __init__(self, memory_provider: ChromaDBContextProvider):
        self.memory = memory_provider  # Dependency injection
    
    async def store_knowledge(self, content: str, metadata: Dict[str, Any]):
        await self.memory.store(content=content, metadata=metadata)
    
    async def retrieve_knowledge(self, query: str) -> List[Dict[str, Any]]:
        return await self.memory.query(query)

# ❌ Wrong - Direct database access (violates MAF SDK!)
import chromadb

class MyAgent:
    def __init__(self):
        # Direct ChromaDB access bypasses MAF SDK's memory layer!
        self.db = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.db.get_or_create_collection("knowledge")
    
    async def store_knowledge(self, content: str):
        self.collection.add(documents=[content])  # Not MAF SDK compliant!
```

**Rationale**:
- Ensures portability across MAF deployments
- Enables enterprise governance and unified telemetry
- Allows pluggable memory backends
- Maintains MAF SDK's durability guarantees

### 4. State Management with AgentThread (REQUIRED)

Use MAF SDK's `AgentThread` for temporal state management across multi-turn conversations.

```python
from agent_framework import AgentThread, ChatAgent

# ✅ Correct - Uses AgentThread
class MyAgent:
    def __init__(self):
        self.threads: Dict[str, AgentThread] = {}
    
    def get_or_create_thread(self, conversation_id: str) -> AgentThread:
        if conversation_id not in self.threads:
            self.threads[conversation_id] = AgentThread(
                message_store=PostgreSQLMessageStore(session_id=conversation_id)
            )
        return self.threads[conversation_id]
    
    async def process(self, message: str, conversation_id: str):
        thread = self.get_or_create_thread(conversation_id)
        response = await self.sdk_agent.run(message, thread=thread)
        return response.text
```

**Current Status**: ✅ Project is compliant (verified in audit).

### 5. Workflows with WorkflowBuilder (REQUIRED)

Multi-agent orchestration MUST use MAF SDK's `WorkflowBuilder`, `Executor`, and `Edge` classes.

```python
from agent_framework import WorkflowBuilder

# ✅ Correct - Uses MAF SDK workflow components
def create_workflow(agent1, agent2):
    builder = WorkflowBuilder(name="MyWorkflow")
    builder.add_agent(agent1, id="agent_1")
    builder.add_agent(agent2, id="agent_2")
    builder.set_start_executor(agent1)
    builder.add_edge(agent1, agent2)
    builder.with_checkpointing(checkpoint_storage)
    return builder.build()

# ❌ Wrong - Custom workflow logic (bypasses MAF SDK!)
class CustomWorkflow:
    def __init__(self, agent1, agent2):
        self.agents = [agent1, agent2]  # Don't reinvent the wheel!
    
    async def run(self, input_data):
        result1 = await self.agents[0].process(input_data)
        result2 = await self.agents[1].process(result1)
        return result2
```

**Current Status**: ✅ Project is compliant (verified in audit).

---

## Common Patterns

### Pattern 1: Creating a New Agent

```python
from agent_framework import ChatAgent

class MyNewAgent:
    """Brief description of agent role."""
    
    def __init__(self, dependencies):
        self.sdk_agent = ChatAgent(
            name="MyAgent",
            instructions="Clear, specific instructions",
            tools=[...]  # Only necessary tools
        )
    
    async def handle(self, input_data):
        """Main entry point."""
        response = await self.sdk_agent.chat(input_data)
        return response
```

### Pattern 2: Adding a New Tool

```python
async def my_new_tool(param: str) -> str:
    """
    Brief description.
    
    Args:
        param: What it means
    
    Returns:
        What it returns
    """
    # Implementation
    return result
```

**Register in**: `src/config/tool_registry.py`

### Pattern 3: Database Migration

```sql
-- File: src/persistence/migrations/YYYY_MM_DD_description.sql
CREATE TABLE my_new_table (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    ...
);

CREATE INDEX idx_my_table_field ON my_new_table(field);
```

**Run via**: `python scripts/apply_migrations.py`

---

## Tools and Workflows

### Development Commands

```bash
# Start the entire stack
./scripts/start_node.sh

# Run tests
pytest tests/

# Apply database migrations
docker exec maf-agent python scripts/apply_migrations.py

# Check logs
docker logs maf-agent
docker logs maf-ui

# Stop everything
docker compose down
```

### Testing Workflow

1. **Unit Tests**: `tests/unit/` - Fast, isolated
2. **Integration Tests**: `tests/integration/` - Test agent interactions
3. **Verification Scripts**: `tests/verification/` - End-to-end validation

### Git Workflow

- **Branches**: Feature branches off `main`
- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
- **PRs**: All changes via pull request

---

## File Organization

```
src/
├── agents/          # Agent implementations
├── api/             # FastAPI endpoints
├── persistence/     # Database clients, Context Providers
├── services/        # Business logic
├── tools/           # Agent tools
└── ui/              # Streamlit app

docker/              # Dockerfiles
config/              # Configuration files
scripts/             # Utility scripts
tests/               # Test suite
docs/                # Documentation
```

---

## Security Guidelines

### API Keys

- **Never commit** API keys to Git
- Store in `.env` file (gitignored)
- Load via `pydantic.BaseSettings`

### Database

- **Parameterized queries** only (prevent SQL injection)
- Use `asyncpg` for PostgreSQL
- Connection pooling for production

### Docker

- **Read-only mounts** for sensitive code (Phase 10+)
- Network isolation between services
- No privileged containers

---

## Performance Considerations

### LLM Calls

- **Batch requests** when possible
- Use streaming for long responses
- Cache common queries (future)

### Database

- **Index frequently queried fields**
- Use `EXPLAIN ANALYZE` for slow queries
- Connection pooling

### UI

- **React Flow** for agent graph (optimized for large graphs)
- Lazy loading for documentation
- Debounce user input in chat

---

## Common Gotchas

1. **Async**: Always use `await` for I/O operations
2. **Docker Networking**: Use service names (`maf-postgres`), not `localhost`
3. **Migrations**: Run in order, never modify old migrations
4. **LiteLLM**: Requires `LITELLM_MASTER_KEY` environment variable
5. **Ollama**: Needs GPU access via `--gpus all` in docker-compose

---

## Documentation System Usage

### When to Update Documentation

Agents should update documentation in these scenarios:

1. **Architecture Changes** → Update `architecture/CURRENT.md`
2. **New Feature** → Update `MANIFEST.yaml`, create guide if needed
3. **Phase Complete** → Archive in `planning/ARCHIVE.md`, update `planning/CURRENT.md`
4. **Audit/Feedback** → Add to `feedback/CURRENT.md`
5. **Design Decision** → Add ADR to `architecture/DECISIONS.md`

### Documentation Structure

```
docs/
├── .ai/                      # Agent workspace
│   ├── MANIFEST.yaml        # Features + templates
│   ├── AGENTS.md            # Agent roles
│   └── GUIDELINES.md        # This file
├── planning/
│   ├── CURRENT.md           # Active phase
│   └── ARCHIVE.md           # History
├── feedback/
│   ├── CURRENT.md           # Active feedback
│   └── ARCHIVE.md           # Resolved feedback
├── architecture/
│   ├── CURRENT.md           # System state
│   └── DECISIONS.md         # ADRs
├── guides/                  # How-to docs
├── why/                     # Rationale docs
├── research/                # Reference material (READ-ONLY)
└── vision/                  # Future plans
```

### Using Templates

Templates are defined in `MANIFEST.yaml`. To create new documentation:

1. Check `MANIFEST.yaml` for appropriate template
2. Use template structure
3. Add YAML frontmatter with access rules
4. Update affected docs (e.g., `INDEX.md`, `CURRENT.md`)

### Generic vs. Project-Specific

**Keep Generic (Template-Ready):**
- `.ai/GUIDELINES.md` - Use placeholders like `[Project Name]`
- `.ai/AGENTS.md` - Use "Local LLM" instead of "Llama 3.1 8B"
- Templates in `MANIFEST.yaml`

**Be Specific (Implementation Details):**
- `README.md` - Can mention specific models, ports, hardware
- `architecture/CURRENT.md` - Document exact configuration
- `guides/*` - Step-by-step for THIS stack

**Why?** Generic files become templates for future projects. Specificity helps current users.

---

## Agent-Specific Behaviors

### Documentation Agent (Domain Lead - Docs)

**Responsibilities:**
- Update documentation when features change
- Maintain CURRENT vs ARCHIVE patterns
- Ensure YAML frontmatter accuracy

**Workflow:**
1. Detect feature change (from `MANIFEST.yaml`)
2. Identify affected docs (listed in feature definition)
3. Apply appropriate template
4. Update cross-references

### All Agents

**When starting work:**
1. Check `planning/CURRENT.md` - What's the active phase?
2. Read implementation plan (linked in CURRENT.md)
3. Update task tracking as you progress

**When completing phase:**
1. Verify success criteria met
2. Update `architecture/CURRENT.md` with changes
3. Archive phase in `planning/ARCHIVE.md`
4. Create new `planning/CURRENT.md` for next phase

---

## Quick Navigation

**Need to know:**
- **What am I working on?** → `planning/CURRENT.md`
- **What happened before?** → `planning/ARCHIVE.md`
- **Why does X exist?** → `why/RATIONALE.md`
- **How do I do X?** → `guides/`
- **What is the system?** → `architecture/CURRENT.md`
- **Why was X decided?** → `architecture/DECISIONS.md`
- **What needs fixing?** → `feedback/CURRENT.md`
- **What's the vision?** → `vision/FUTURE.md`
- **Reference material?** → `research/INDEX.md`

---

## Updates to This Document

**When to update:**
- Coding standards change (requires human approval for MAF SDK standards)
- New architectural pattern emerges
- Common gotcha identified

**Who can update:**
- Agents (for non-MAF SDK patterns)
- Humans (for MAF SDK standards, critical changes)

**Process:**
1. Propose change (create diff)
2. Get approval if needed
3. Update this file
4. Notify in changelog or feedback doc
