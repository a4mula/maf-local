---
access: read-write
audience: agents | humans
update_trigger: significant_design_decision
managed_by: Humans or agents via ADR template
---

# Architecture Decision Records (ADRs)

> [!NOTE]
> This document tracks **significant design decisions** and their rationale.  
> For the current system state, see [`CURRENT.md`](./CURRENT.md).

---

## ADR-001: Hierarchical Agent System (Phase 1)

**Date:** 2025-10-01  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead

### Context

Initial requirement was to build a coding assistant. Two approaches considered:
1. Single monolithic agent (like existing assistants)
2. Hierarchical multi-agent system with specialized roles

### Decision

Adopted 4-tier hierarchical architecture:
- **Tier 1:** Liaison (user interface, intent filtering)
- **Tier 2:** Project Lead (orchestration, planning)
- **Tier 3:** Domain Leads (specialized domains: Dev, QA, Docs)
- **Tier 4:** Executors (atomic task execution)

### Consequences

**✅ Benefits:**
- Separation of concerns prevents cognitive overload
- Auditable decision chain (all escalations logged)
- Scalable (add new domain leads without refactoring)
- Resilient (checkpoints enable resume after human intervention)

**⚠️ Trade-offs:**
- More complex than single agent
- Increased inter-agent communication overhead
- Requires workflow orchestration (MAF SDK)

---

## ADR-002: Microsoft Agent Framework (MAF SDK) (Phase 1)

**Date:** 2025-10-01  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead

### Context

Needed a framework to support hierarchical agents with durable workflows. Options:
1. Build custom workflow engine
2. Use LangGraph
3. Use Microsoft Agent Framework (MAF SDK)

### Decision

Selected MAF SDK for enterprise-grade workflow orchestration.

### Rationale

- **Checkpointing:** Built-in workflow persistence (resume after failures)
- **Type Safety:** Enforces type hints for tool calling and message passing
- **Enterprise Features:** Unified identity, governance, telemetry
- **Pluggable:** Context Providers, CheckpointStorage, AgentThreads

### Consequences

**✅ Benefits:**
- Workflow durability out-of-the-box
- Enterprise deployment path
- Strong architectural patterns (prevents drift)

**⚠️ Trade-offs:**
- Learning curve for MAF SDK patterns
- Must adhere to MAF SDK standards (Context Providers, WorkflowBuilder)

---

## ADR-003: FOSS-First Philosophy (Phase 0)

**Date:** 2025-09-15  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead

### Context

LLM hosting options:
1. Cloud-only (OpenAI, Anthropic)
2. Local-only (Ollama)
3. Hybrid (local primary, cloud fallback)

### Decision

Hybrid approach: **Ollama (local) primary, Gemini 2.0 Flash (cloud) fallback** via LiteLLM Proxy.

### Rationale

- **Privacy:** Local models = zero data leakage
- **Cost:** Local inference = $0 per request
- **Reliability:** Cloud fallback ensures uptime
- **Performance:** GPU-accelerated Ollama for low latency

### Consequences

**✅ Benefits:**
- No API costs for routine tasks
- Full control over model versions
- Works offline (with degraded functionality)

**⚠️ Trade-offs:**
- Requires GPU (NVIDIA, 8GB+ VRAM)
- Local model capability < GPT-4 class
- Increased infrastructure complexity (Docker services)

---

## ADR-004: PostgreSQL + ChromaDB Dual Persistence (Phase 2-4)

**Date:** 2025-10-15  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead

### Context

Need both structured (audit logs, governance) and unstructured (RAG knowledge) persistence.

### Decision

- **PostgreSQL:** Audit logs, checkpoints, agent metadata, drift detection
- **ChromaDB:** Vector embeddings for RAG (project context, documentation)

### Rationale

- PostgreSQL: ACID guarantees for governance
- ChromaDB: Optimized for semantic search
- Both lightweight and FOSS

### Consequences

**✅ Benefits:**
- Right tool for each job
- Both integrate with MAF SDK (CheckpointStorage, Context Providers)

**⚠️ Trade-offs:**
- Two databases to maintain
- Coordination required for cross-database queries (future)

---

## ADR-005: Streamlit + Next.js Dual UI (Phase 8)

**Date:** 2025-11-10  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead

### Context

UI requirements:
1. **Liaison home base:** Simple chat interface
2. **Agent graph visualization:** Real-time activity monitoring

### Decision

- **Streamlit (`:8501`):** Chat interface (rapid prototyping, Python-native)
- **Next.js (`:3000`):** Agent graph with React Flow (rich interactivity)

### Rationale

- Streamlit = fastest path for chat UI
- Next.js = best library support for graph visualization (React Flow)
- Both share same FastAPI backend (`/api/agent_api.py`)

### Consequences

**✅ Benefits:**
- Right UI framework for each use case
- Shared backend reduces duplication

**⚠️ Trade-offs:**
- Two frontend codebases to maintain
- State synchronization complexity

---

##ADR-006: Phase 10 Multi-Project Pivot (Principle of Least Authority)

**Date:** 2025-11-20  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead, Human

### Context

Original vision: DevStudio modifies its own source code.  
**Problem:** Agents with write access to their own source = catastrophic risk (self-modification, deletion).

### Decision

**Architectural Pivot:** Transform DevStudio from self-modifying to **multi-project IDE backend**.

**Key Changes:**
1. **Read-only source mount:** DevStudio source code mounted read-only in Docker
2. **Workspaces directory:** Projects live in `/workspaces/{project_id}/`
3. **Project isolation:** Each project gets scoped database (project_id), isolated ChromaDB collection
4. **Principle of Least Authority (PoLA):** Agents only access tools they need, projects they're assigned to

### Rationale

- **Security:** Prevents accidental or malicious self-modification
- **Scalability:** Manage multiple client projects, not just DevStudio itself
- **Enterprise-ready:** Aligns with MAF SDK's multi-tenant patterns
- **Audit-friendly:** Clear separation between system code and project artifacts

### Consequences

**✅ Benefits:**
- Eliminates catastrophic failure mode
- Enables commercial use (service multiple projects)
- Cleaner testing (DevStudio code stable, projects ephemeral)

**⚠️ Trade-offs:**
- Complexity increase (project registry, session management)
- Requires FileTreeReader tool for project context injection
- read-only mount = no self-upgrade path (requires manual rebuild)

**Implementation:** Phase 10 (blocked on MAF SDK compliance)

---

## ADR-007: Documentation Architecture (CURRENT + ARCHIVE Pattern)

**Date:** 2025-11-21  
**Status:** ✅ ACCEPTED  
**Deciders:** Project Lead, Human

### Context

Documentation proliferation issues:
- Inconsistent patterns (some categories had CURRENT/ARCHIVE, others didn't)
- Redundancy (`tutorials/` vs `how-to/`)
- Unclear relationships (vision vs planning vs roadmap)
- Messy `.ai/` folder (7 files, inconsistent naming)

### Decision

Apply **universal CURRENT + ARCHIVE pattern** across all temporal documentation:

**Temporal (2-file pattern):**
- `planning/CURRENT.md` + `planning/ARCHIVE.md`
- `feedback/CURRENT.md` + `feedback/ARCHIVE.md`
- `architecture/CURRENT.md` + `architecture/DECISIONS.md` (this file)

**Reference (single-file pattern):**
- `why/RATIONALE.md` (all "why" questions)
- `vision/FUTURE.md` (all aspirations)
- `research/INDEX.md` (catalog of research docs)

**Consolidations:**
- `.ai/`: 7 files → 3 files (MANIFEST.yaml, GUIDELINES.md, AGENTS.md)
- `tutorials/` + `how-to/` → `guides/`
- `explanation/` → `why/`

### Rationale

- **DRY Principle:** Eliminate redundant directories
- **Agent Navigation:** Clear patterns (`planning/CURRENT.md` = always what's happening now)
- **Temporal Clarity:** CURRENT vs ARCHIVE prevents file proliferation
- **Scalability:** Pattern applies to any new documentation category

### Consequences

**✅ Benefits:**
- Agents know exactly where to look
- Prevents documentation sprawl
- Clear migration path (CURRENT → summarize → ARCHIVE)
- Reusable template for future projects

**⚠️ Trade-offs:**
- Large initial migration (16+ files affected)
- Requires discipline to maintain patterns

---

## Template: Adding New ADR

When adding a new architecturedecision, use this format:

```markdown
## ADR-XXX: [Title]

**Date:** YYYY-MM-DD  
**Status:** PROPOSED | ACCEPTED | DEPRECATED  
**Deciders:** [Who made this decision]

### Context

[What prompted this decision? What problem are we solving?]

### Decision

[What did we decide? Be specific.]

### Rationale

[Why did we choose this option?]

### Consequences

**✅ Benefits:**
- [Positive outcome 1]
- [Positive outcome 2]

**⚠️ Trade-offs:**
- [Cost or limitation 1]
- [Cost or limitation 2]
```
