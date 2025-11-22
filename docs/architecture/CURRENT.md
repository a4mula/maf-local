# Current Architecture

**Last Updated:** November 22, 2025

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

```
User
  ↓
LiaisonAgent (Tier 1)
  ↓
ProjectLeadAgent (Tier 2)
  ↓
DomainLeadAgent (Tier 3) [Development, QA, Docs]
  ↓
ExecutorAgent (Tier 4) [Coder, Tester, Writer]
  ↓
FileWriterAgent (Specialized) [PL-Approved Disk Writes]
```

**Current Implementation Status:**

> [!CAUTION]
> **Critical Gap:** Agents exist as classes but function as **chatbots**, not workflow orchestrators.

- ✅ Liaison and Project Lead exist as `ChatAgent` instances
- ⚠️ They **pass messages**, not create MAF Workflow Graphs
- ❌ Domain Leads exist but are **not wired** to Project Lead
- ❌ Executors exist but are **never invoked**
- ❌ FileWriterAgent **does not exist** yet
- ✅ Intent classification works (Question vs. Idea)
- ⚠️ Context injection uses **blocking sync I/O** (`os.walk`, violates async mandate)

**Comprehensive Audit Findings:** See [`feedback/feedback_full.md`](../feedback/feedback_full.md) for 16-component technical analysis.

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

## Security & Isolation

> [!WARNING]
> **Current PoLA Status:** VIOLATED

### Intended Design (Phase 10):
1. **Read-Only Source**: Agents cannot modify `/app/src` (DevStudio source).
2. **Workspace Isolation**: Agents operate in `/workspaces/{project_id}/`.
3. **Context Scoping**: All persistence operations (DB, Vector) are scoped by `project_id`.

### Current Reality (from Comprehensive Audit):
- ❌ Liaison and ProjectLead **directly access filesystem** (lines 18 in both files)
- ❌ No FileWriterAgent to enforce approval workflow
- ❌ `code_tools.py` uses **unchecked `exec()`** (RCE vulnerability)
- ⚠️ Hardcoded security defaults (`sk-1234`, `maf_user:maf_pass`)

**Resolution Plan:** See [`planning/CURRENT.md`](../planning/CURRENT.md) Phase 0 (Critical Infrastructure Fixes).

## Current Limitations

> [!CAUTION]
> **The system is architecturally sound but functionally incomplete.**

### Critical Gaps (from Comprehensive Audit):

1. **LLM Adapter Cannot Parse Tool Calls** 🛑
   - `litellm_client.py` returns only text, not tool call objects
   - **Impact:** Agents cannot use ANY tools
   - **Workaround:** `core_agent.py` uses brittle string parsing

2. **No Secure File Writing** 🛑
   - `code_tools.py` has no `write_file` tool
   - **Impact:** System cannot generate code files
   - **Security:** Unchecked `exec()` poses RCE risk

3. **Delegation Stubbed** ⚠️
   - `communication_tools.py` has empty `send_message` stub
   - **Impact:** ProjectLead cannot delegate to Domain Leads

4. **Async I/O Violations** ⚠️
   - Liaison and PL use synchronous `os.walk` during init
   - **Impact:** Blocks event loop, wastes LLM tokens

### Strong Components (Audit "Bright Spots"):

- ✅ `chromadb_context_provider.py` - Perfect MAF SDK compliance
- ✅ `project_context.py` - Concurrency-safe, strict enforcement
- ✅ `universal_tools.py` - Sophisticated PoLA framework
- ✅ `governance_agent.py` - Textbook async implementation
- ✅ `context_retrieval_agent.py` - Clean dependency injection

**Metaphor from Audit:** *"The shape of a car (class hierarchy, interfaces) exists, but the engine and steering wheel (Tool Client, Delegation, Execution) are missing or broken."*

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
