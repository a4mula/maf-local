# Current Architecture

**Last Updated:** November 23, 2025

## Overview

The Hierarchical MAF Studio is a local-first, GPU-accelerated development environment for multi-agent systems. Following the **Phase 10 Infrastructure Pivot** (Nov 22, 2025), it now runs as a **Host-Native application** with infrastructure in Docker.

> [!IMPORTANT]
> **Deployment Model:** Agent API and Streamlit UI run natively on the host (Python venv), while infrastructure services (Postgres, Ollama, ChromaDB, LiteLLM) run in Docker containers.

## System Components

### 1. Core Services

| Service | Port | Deployment | Status |
| :--- | :--- | :--- | :--- |
| **Ollama** | 11434 | Docker | ✅ Running |
| **LiteLLM Proxy** | 4000 | Docker | ✅ Running |
| **PostgreSQL** | 5432 | Docker | ✅ Running |
| **ChromaDB** | 8000 | Docker | ✅ Running |
| **Prometheus** | 9093 | Docker | ✅ Running |
| **Grafana** | 3000 | Docker | ✅ Running |
| **Streamlit UI** | 8501 | **Host** (via `run_studio.sh`) | ✅ Running |
| **Next.js Graph** | 3001 | Host | ✅ Running |
| **Agent API** | 8002 | **Host** (via `run_studio.sh`) | ✅ Running |

**Startup Command:** `./run_studio.sh` (creates .venv, installs deps, launches Agent API + UI)

### 2. Agent Hierarchy

**Current Architecture (Simplified MVP):**

```
User
  ↓
LiaisonAgent (Tier 1) - Intent Classification, Message Routing
  ↓
ProjectLeadAgent (Tier 2) - Decision Making, Tool Execution via MAF ChatAgent
```

**Implementation Status:**

> [!NOTE]
> **Architecture Philosophy:** Following "MVP-first" approach - prove core mechanics work before adding complexity.

- ✅ Liaison and Project Lead implemented using MAF's `ChatAgent`
- ✅ MAF-compliant tool execution via `@use_function_invocation` decorator
- ✅ Tools registered as `AIFunction` objects
- ✅ Intent classification works (Question vs. Idea)
- ✅ File generation capability via `write_file` tool
- ✅ LiteLLMChatClient extends `BaseChatClient` properly

**Deleted Agents (Emergency Refactor - Nov 2025):**
- ❌ DomainLeadAgent (removed in simplification phase)
- ❌ ExecutorAgent (removed in simplification phase)
- ❌ GovernanceAgent (removed in simplification phase)
- ❌ ContextRetrievalAgent (removed in simplification phase)
- ❌ ArtifactManagerAgent (removed in simplification phase)

**Rationale:** Focused on working execution layer before rebuilding hierarchy. See `walkthrough.md` for refactor details.

### 3. Data Persistence

**MAF SDK Compliance:** ✅ All persistence layers use MAF SDK interfaces (as of Phase 10.1)

| Layer | Technology | Interface | Status |
| :--- | :--- | :--- | :--- |
| **Structured Data** | PostgreSQL | `MessageStoreProvider` | ✅ Operational |
| **Vector Data** | ChromaDB | `ChromaDBContextProvider` | ✅ MAF SDK-compliant (world-class) |
| **Checkpoints** | PostgreSQL | `CheckpointStorage` | ✅ Operational |
| **File Storage** | Host Filesystem | Native paths | ✅ **Direct access** (Host-Native) |

#### Project Context Management (Phase 10)

**Implementation:** [`src/persistence/project_context.py`](file:///home/robb/projects/maf-local/src/persistence/project_context.py)

**Purpose:** Enforces strict isolation between projects using thread-local storage.

**Key Design:**
- ✅ `ProjectContextManager`: Thread-safe storage for `project_id` (concurrency-safe using `contextvars`)
- ✅ **Automatic Injection**: `ChromaDBContextProvider` automatically injects `project_id` into metadata
- ✅ **Automatic Filtering**: All queries are scoped to the active `project_id`

**Quality:** Identified as **world-class implementation** in comprehensive audit.

### 4. File Structure

```
maf-local/
├── config/           # LiteLLM, Prometheus configs
├── docker/           # Dockerfiles (infrastructure only)
├── docs/             # Documentation
│   ├── planning/     # Roadmap, CURRENT re-alignment plan
│   ├── vision/       # Ideal state
│   ├── feedback/     # Audits and feedback
│   └── .ai/          # Agent workspace (guidelines, manifest)
├── scripts/          # Startup, migrations
├── src/              # Agent source code
│   ├── agents/       # Agent implementations
│   ├── api/          # FastAPI endpoints
│   ├── persistence/  # DB clients
│   └── tools/        # Agent tools
├── tests/            # Verification scripts
├── ui-next/          # Next.js visualization
├── run_studio.sh     # Host-Native startup script
└── .venv/            # Python virtual environment (Host-Native)
```

## Security & File I/O

### Current Implementation:

**File Writing:**
- ✅ Sandboxed `write_file` tool in `src/tools/code_tools.py`
- ✅ Path validation prevents directory traversal
- ✅ Operations scoped to project root via `_is_safe_path()`

**Code Execution:**
- ⚠️ `execute_code` tool uses `exec()` for Python evaluation
- ⚠️ Isolated via `io.StringIO` redirection
- 🔒 Future: Consider containerized sandbox

**Authentication:**
- ⚠️ LiteLLM uses `LITELLM_MASTER_KEY` from `.env`
- ⚠️ PostgreSQL uses credentials from `.env`
- 🔒 Recommended: Rotate default credentials in production

## Recent Improvements (November 2025)

> [!NOTE]
> **Emergency Refactor Complete:** All critical execution layer issues resolved.

### Fixed Issues:

1. **✅ Tool Execution Working**
   - `LiteLLMChatClient` now extends `BaseChatClient`
   - Applied `@use_function_invocation` decorator for automatic tool execution
   - MAF framework handles the execution loop natively

2. **✅ File Generation Operational**
   - `write_file` tool implemented with path sandboxing
   - Integration tests confirm end-to-end flow works
   - Files successfully created on disk

3. **✅ Architecture Simplified**
   - Removed unused agents (DomainLead, Executor, etc.)
   - Focus on proven working components
   - Eliminated "architecture astronaut" complexity

### Current Limitations:

1. **Limited Hierarchy** ⚠️
   - Only 2-tier architecture (Liaison → ProjectLead)
   - Future: Rebuild Domain Leads with proper MAF workflows

2. **Basic Tool Set** ⚠️
   - Current tools: `write_file`, `execute_code`
   - Future: Add code analysis, testing, deployment tools

3. **Manual Testing** ⚠️
   - Integration tests verify structure
   - Full E2E workflow testing requires real LLM interaction

## API Endpoints

### Agent API (`http://localhost:8002`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send message to Liaison Agent |
| `GET` | `/api/agents/status` | Get real-time agent hierarchy |

### Planned (Phase 10)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/projects/list` | List managed projects |
| `POST` | `/api/sessions/start/{project_id}` | Start session for a project |

## Next Steps

See [Phase 10 Architectural Mandate](../feedback/phase_10_architectural_mandate.md) for the critical pivot required before further development.
