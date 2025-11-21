---
access: read-write
audience: agents | humans
update_trigger: vision_change | long_term_goal_added
managed_by: Human (strategic decisions)
---

# Vision: FUTURE

> [!NOTE]
> This document captures the **long-term vision** for MAF Local.  
> For current implementation status, see [`planning/CURRENT.md`](../planning/CURRENT.md) and [`architecture/CURRENT.md`](../architecture/CURRENT.md).

---

## Short-Term Goals (Next 3-6 Months)

### Phase 10.1: MAF SDK Compliance ✅

**Goal:** Ensure full compliance with Microsoft Agent Framework (MAF SDK) standards.

**Status:** 🚧 IN PROGRESS

**Key Deliverables:**
- Implement `ChromaDBContextProvider` (MAF SDK Context Providers interface)
- Refactor `ContextRetrievalAgent` for dependency injection
- Update coding standards in documentation

###Completed Phase 10: Multi-Project DevStudio 🎯

**Goal:** Transform DevStudio from single-project to multi-project IDE backend.

**Vision:** The DevStudio becomes a **service** that manages **external client projects**, not its own source code.

**Key Changes:**
1. **Principle of Least Authority (PoLA):**
   - Read-only mount of DevStudio source code
   - Projects live in `/workspaces/{project_id}/`
   - Agents cannot modify system code

2. **Project Isolation:**
   - Project registry (PostgreSQL)
   - Scoped ChromaDB collections per project
   - Session-based project switching

3. **Generic Project Manager UI:**
   - Project list view
   - One-click project selection
   - Project-specific file trees injected via `FileTreeReader` tool

**Why This Matters:**
- **Security:** Eliminates self-modification risk
- **Scalability:** Manage multiple client codebases
- **Commercial Viability:** DevStudio as a service (not just self-contained tool)

---

## Medium-Term Vision (6-12 Months)

### Advanced Context Management

**Goal:** Fully utilize ChromaDB for intelligent context retrieval.

**Current State:** ChromaDB infrastructure exists but is underutilized.

**Vision:**
- Automatic project documentation ingestion on registration
- Semantic search for relevant code snippets
- Agent-driven "just-in-time" context injection based on task
- Multi-modal embeddings (code + docs + commit history)

### Agent Specialization

**Goal:** Expand domain leads beyond Dev/QA/Docs.

**Planned Additions:**
- **Security Lead:** SAST/DAST analysis, vulnerability scanning
- **Performance Lead:** Profiling, optimization recommendations
- **UX Lead:** Accessibility audits, design system compliance

**Rationale:** As projects grow, specialized expertise prevents cognitive overload for Domain Leads.

### Workflow Templates

**Goal:** Pre-built workflows for common tasks.

**Examples:**
- "Full-Stack Feature" workflow (backend → frontend → tests → docs)
- "Bug Fix" workflow (reproduce → fix → regression test → deploy)
- "Refactoring" workflow (plan → execute → verify no behavior change)

**Why:** Reduce Project Lead planning overhead for routine tasks.

---

## Long-Term Aspirations (1+ Years)

### The Hierarchical MAF Studio: Ideal State

![Hierarchical Agent Visual](/home/robb/.gemini/antigravity/brain/b3aafb48-2f49-4898-8f0f-3a20c189122b/uploaded_image_1763726278986.png)

**Vision:** A resilient, auditable **DevStudio Service Node** that:

1. **Manages External Projects** as isolated execution environments
2. **Strictly Adheres to PoLA** (Principle of Least Authority)
3. **Uses FOSS Stack** (Ollama, PostgreSQL, ChromaDB) for local-first operation
4. **Provides Generic Project Manager UI** for selecting and managing multiple client codebases

### The Total Loop & Justification

The system operates on a **four-tiered hierarchy** designed to prevent **cognitive overload**.

#### 1. Idea Capture (Liaison ↔ Project Lead)

The **Liaison (L)** focuses *only* on user intent. It hands off the raw idea to the **Project Lead (PL)**, which is the sole **technical decision-maker**. The PL loops with the L for clarity until a **structured, non-boilerplate** plan is achieved.

#### 2. Orchestration & Governance (Project Lead → DLs)

The PL takes the clarified plan and translates it into a dynamic **MAF Workflow Graph**, defining the required **Pillars** (e.g., Development, QA). The PL then instantiates and delegates work to the specialized **Domain Leads (DLs)**, injecting only the necessary **pillar-specific context**.

#### 3. Execution & Atomic Tasking (DL → Executors)

The **DLs** manage the **Executor Agents** (Coders, Testers). Executors perform a single, atomic task with minimal context.

#### 4. Bottom-Up Ambiguity Resolution

If an Executor encounters ambiguity (e.g., "First-person or Third-person?"), it follows a mandatory escalation: **Executor → DL → PL → L → User**. The **Project Lead** updates the **Governance Agent (PostgreSQL)** with the authoritative decision, and the workflow resumes from a **Checkpoint**.

**Justification:** This hierarchy ensures **auditability** (every decision is tracked by the PL) and **resilience** (the workflow can pause, save state using MAF's CheckpointStorage, and resume after human intervention).

### Enterprise Features

**When MAF Local matures:**

1. **Multi-Tenancy:**
   - Multiple users, each with their own project workspaces
   - Azure AD / OAuth integration for identity
   - Role-based access control (RBAC)

2. **Cloud Deployment:**
   - Azure Container Instances for scalable agent execution
   - Cosmos DB as alternative to local PostgreSQL
   - Azure Blob Storage for artifacts

3. **CI/CD Integration:**
   - GitHub Actions / Azure DevOps pipelines trigger workflows
   - Automated PR creation for agent-generated code
   - Drift detection on every commit

4. **Advanced Governance:**
   - Compliance policies (e.g., "no DB schema changes without approval")
   - Automated audit reports (weekly summaries of agent activity)
   - Cost tracking for cloud LLM usage

### Self-Evolution

**Controversial Vision:** Can DevStudio **safely** upgrade itself?

**Challenge:** Read-only source mount prevents self-modification.

**Possible Solutions:**
1. **Staged Upgrade Path:**
   - Agents generate upgrade plan (new Docker image, migrations)
   - Human reviews and approves
   - Orchestrator rebuilds DevStudio container

2. **Hot-Swappable Agents:**
   - Core orchestration remains stable
   - Individual agents updated via plugin system
   - Version-pinned agent images

3. **Community Contribution:**
   - Agents propose PRs to upstream MAF Local repo
   - Human maintainers review and merge
   - Standard Docker rebuild for updates

**Decision:** Not prioritized until Phase 15+ (must first prove multi-project stability).

---

## Alignment with MAF SDK Ecosystem

**Current Status:** 🟡 70% aligned (1 critical violation)

**Vision:** **100% MAF SDK Compliant**

**What This Unlocks:**
- Seamless integration with Microsoft Agent Framework updates
- Access to MAF SDK enterprise features (unified identity, governance)
- Interoperability with other MAF-based agent systems
- Contribution to MAF SDK community (plugins, patterns)

**Roadmap:**
- ✅ Phase 10.1: Fix Context Provider violation
- 📋 Phase 11: Contribute `ChromaDBContextProvider` to MAF SDK (if useful)
- 📋 Phase 12: Implement optional Azure integrations (Context Providers for Azure Blob, Cosmos DB)

---

## Success Metrics (Long-Term)

By end of 2026, MAF Local should achieve:

- [ ] **10+ active projects** managed simultaneously
- [ ] **95% MAF SDK compliance** (verified via automated audits)
- [ ] **< 5% cloud LLM usage** (local models handle majority of tasks)
- [ ] **Zero self-modification incidents** (PoLA enforced)
- [ ] **Community adoption** (5+ external contributors to repo)
- [ ] **Enterprise pilot** (1+ company using MAF Local in production)

---

## Inspirations & References

- **MAF SDK Documentation:** https://learn.microsoft.com/en-us/agent-framework/
- **MAF Workflow Video:** https://www.youtube.com/watch?v=KQ09sMHeFQY
- **Hierarchical Agent Patterns:** Inspired by org charts (CEO → Managers → Individual Contributors)
- **PoLA (Principle of Least Authority):** Security best practice from capability-based security research

---

## Contributing to This Vision

This vision is a living document. If you have ideas:

1. **Internal:** Add to `feedback/CURRENT.md` or discuss in planning sessions
2. **External:** Open an issue in the GitHub repo
3. **Agents:** If significant, trigger an update via `DocUpdatePlanner` tool

**Decision Authority:** Human (strategic vision) with agent input (feasibility, implementation sketches)
