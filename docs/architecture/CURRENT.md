# Current Architecture

**Last Updated:** November 21, 2025

## Overview

The Hierarchical MAF Studio is a local-first, GPU-accelerated development environment for multi-agent systems. It currently operates as a **single-project system** but is planned to transition to a **multi-project DevStudio service** (Phase 10).

## System Components

### 1. Core Services

| Service | Port | Purpose | Status |
| :--- | :--- | :--- | :--- |
| **Ollama** | 11434 | Local LLM inference (Llama 3.1 8B) | ✅ Running |
| **LiteLLM Proxy** | 4000 | Unified model API (local + cloud) | ✅ Running |
| **PostgreSQL** | 5432 | Structured data (Audit, Governance, Checkpoints) | ✅ Running |
| **ChromaDB** | 8000 | Vector embeddings (RAG) | ✅ Running |
| **Prometheus** | 9093 | Metrics collection | ✅ Running |
| **Grafana** | 3000 | Metrics visualization | ✅ Running |
| **Streamlit UI** | 8501 | Chat interface | ✅ Running |
| **Next.js Graph** | 3001 | Live agent visualization | ✅ Running |
| **Agent API** | 8002 | FastAPI backend | ✅ Running |

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
```

**Current Implementation:**
- ✅ Liaison, Project Lead, and Domain Lead agents exist
- ✅ Agent Factory wires the hierarchy
- ✅ Context injection (README, file tree) is generic
- ✅ Intent classification (Question vs. Idea)

### 3. Data Persistence

**MAF SDK Compliance:** ✅ All persistence layers use MAF SDK interfaces (as of Phase 10.1)

| Layer | Technology | Interface | Status |
| :--- | :--- | :--- | :--- |
| **Structured Data** | PostgreSQL | `MessageStoreProvider` | ✅ Operational |
| **Vector Data** | ChromaDB | `ChromaDBContextProvider` | ✅ MAF SDK-compliant |
| **Checkpoints** | PostgreSQL | `CheckpointStorage` | ✅ Operational |
| **File Storage** | Docker Volume | Artifacts | ✅ **Secured** (Phase 10) |

#### Project Context Management (Phase 10)

**Implementation:** [`src/persistence/project_context.py`](file:///home/robb/projects/maf-local/src/persistence/project_context.py)

**Purpose:** Enforces strict isolation between projects using thread-local storage.

**Key Design:**
- ✅ `ProjectContextManager`: Thread-safe storage for `project_id`
- ✅ **Automatic Injection**: `ChromaDBContextProvider` automatically injects `project_id` into metadata
- ✅ **Automatic Filtering**: All queries are scoped to the active `project_id`

### 4. File Structure

```
maf-local/
├── config/           # LiteLLM, Prometheus configs
├── docker/           # Dockerfiles
├── docs/             # Documentation
│   ├── planning/     # Roadmap
│   ├── vision/       # Ideal state
│   └── feedback/     # User feedback logs
├── scripts/          # Startup, migrations
├── src/              # Agent source code
│   ├── agents/       # Agent implementations
│   ├── api/          # FastAPI endpoints
│   ├── persistence/  # DB clients
│   └── tools/        # Agent tools
├── tests/            # Verification scripts
└── ui-next/          # Next.js visualization
```

## Security & Isolation (Phase 10)

> [!IMPORTANT]
> **Principle of Least Authority (PoLA) Enforced**
> 
> As of Phase 10, the DevStudio source code is mounted **Read-Only** to prevent the "Confused Deputy Problem".

### Isolation Mechanisms:
1. **Read-Only Source**: Agents cannot modify `/app/src` (DevStudio source).
2. **Workspace Isolation**: Agents operate in `/workspaces/{project_id}/`.
3. **Context Scoping**: All persistence operations (DB, Vector) are scoped by `project_id`.

## Current Limitations

### Known Issues:
1. **No Multi-Project Support**: Cannot yet manage external codebases (Milestone 2).
2. **RAG Underutilized**: ChromaDB is running but agents don't actively use it for context retrieval.

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
