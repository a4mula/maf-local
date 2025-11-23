# Current Phase: Architectural Re-Alignment

**Last Updated:** 2025-11-22  
**Status:** � **CRITICAL DRIFT CORRECTION IN PROGRESS**

---

## Overview

Following the completion of the Host-Native Infrastructure Pivot (archived), we have **verified** the current state against the documented vision and identified significant architectural drift.

**Current Reality:**
- ✅ Infrastructure is operational (DB, AI models, UI running)
- ✅ Projects can be created and managed
- ❌ Agent hierarchy is not orchestrating workflows (just passing messages)
- ❌ Violates Principle of Least Authority (PoLA)
- ❌ Missing critical layers (Domain Leads, Executors as orchestrators)

**Target State (from `docs/vision/FUTURE.md`):**
- Hierarchical Multi-Agent Framework with workflow orchestration
- Strict role separation (Liaison talks, PL decides, DLs orchestrate, Executors execute)
- PoLA enforcement (only approved agents write files)

---

## Expert Systems Assessment: Emergency Refactor Required

> [!CAUTION]
> **Stop All Feature Development**: Expert review (2025-11-22) identified "Architecture Astronaut Trap" - we built elaborate hierarchy before proving core mechanics work.

**Core Diagnosis:** "Beautiful architecture with no working implementation" - execution layer (LLM adapter, tool calling, file I/O) is stubbed or broken.

**Root Cause:** Premature documentation and complexity. Documented ideal state before proving implementation feasible.

### New Priority Order (Expert-Recommended)

**Week 1: Emergency Fixes** ⚡ (CURRENT FOCUS)
1. Fix `litellm_client.py` tool calling (BLOCKING ALL)
2. Implement sandboxed `write_file` tool (security-critical)
3. Wire ONE end-to-end flow (User → Agent → Tool → Response)
4. Integration tests proving core loop works

**Week 2: Simplification** 🔥
- Delete unused agents (keep Liaison + Projectlead only)
- Remove GovernanceAgent, ArtifactManager temporarily (premature optimization)
- Remove WorkflowBuilder temporarily (add back after MVP)
- Prove simple message passing works

**Week 3: File Generation MVP** 🎯
- ONE working flow: User → Liaison → ProjectLead → FileWriter → Disk
- **Ship it**, then iterate

**Week 4+: Rebuild Incrementally** 📈
- Add DomainLeads back (with tests)
- Add WorkflowBuilder orchestration (with tests)
- Add Executors (with tests)
- Re-integrate governance and observability

**Key Principle:** "Complexity is the enemy of working software" - prove minimal system works, then scale up with tests at each step.

**See:** `feedback/CURRENT.md` - Expert Systems Engineering Assessment for full analysis.

---

## Critical Architectural Gaps

Based on documentation review (`docs/.ai/agents.md`, `docs/vision/FUTURE.md`):

### 1. **Agents as Chatbots, Not Orchestrators** 🔴

**Problem:** 
- `LiaisonAgent` and `ProjectLeadAgent` exist but only pass messages
- No MAF Workflow Graph creation
- No dynamic agent spawning
- No task delegation

**Impact:**
- User says "start implementation" → Agent responds with text, no files created
- Cannot break down complex tasks into workflows
- No parallelization or checkpoint/resume capability

**Required:**
- Integrate MS Agent Framework `Workflow`, `WorkflowGraph`, `Executor` classes
- Implement `ProjectLeadAgent.create_workflow()` method
- Wire Domain Leads into workflow execution

---

### 2. **Missing FileWriterAgent** 🔴

**Problem:**
- Documentation (`docs/.ai/agents.md`) claims Executors have `write_file` tool
- User clarified this is wrong:
  - Executors produce **code artifacts** (strings)
  - Domain Leads **validate** quality
  - Project Lead **approves** write
  - Specialized **FileWriterAgent** executes disk write

**Impact:**
- No clear path from "code generated" → "files on disk"
- PoLA violated (agents accessing filesystem without approval workflow)

**Required:**
- Document `@file-writer` role in `docs/.ai/agents.md`
- Implement `FileWriterAgent` class
- Create approval workflow (Executor → DL → PL → FileWriter)

---

### 3. **PoLA Violations** 🟡

**Problem:**
- `LiaisonAgent` reads from `/app/project_root` (line 18 of `liaison_agent.py`)
- `ProjectLeadAgent` reads from `/app/project_root` (line 18 of `project_lead_agent.py`)
- Agents should have **zero** filesystem access except through approved tools

**Impact:**
- Confused Deputy Problem (agents could modify DevStudio source)
- Violates security requirements from Phase 10

**Required:**
- Remove filesystem access from Liaison and PL
- Context injection should come from approved Context Retrieval Agent
- Only FileWriterAgent (with PL token) can write

---

### 4. **Domain Leads Not Wired** 🟡

**Problem:**
- `DevLeadAgent`, `QALeadAgent`, `DocsLeadAgent` classes exist
- But they're never instantiated or invoked by ProjectLead
- No workflow graph connects them

**Impact:**
- Cannot delegate domain-specific work
- No validation layer between code generation and approval

**Required:**
- ProjectLead creates workflow nodes for each DL based on task requirements
- DLs manage Executor pools
- Results flow back up the hierarchy

---

### 5. **Agent Factory Configuration Antipatterns** 🟡

**Problem (from full audit):**
- Hardcoded `localhost` for ChromaDB instead of `settings.CHROMA_URL`
- Incomplete hierarchical wiring (PL not connected to DLs, DLs not to Executors)
- Missing agents not instantiated (FileWriterAgent, ArtifactManager)

**Impact:**
- Configuration drift from centralized settings
- Breaks dependency injection principle
- System cannot function as designed

**Required:**
- Use `settings.py` for all configuration
- Complete hierarchical wiring
- Instantiate all documented agents

---

### 6. **Infrastructure Fragility** 🟡

**Problem (from full audit):**
- `start_node.sh` uses `sleep 10` instead of health checks
- Runs migrations in `agent` container (contradicts Host-Native design)
- Hardcoded security defaults (`sk-1234`, `maf_user:maf_pass`)

**Impact:**
- Services may not be ready after 10 seconds
- Architectural contradiction (script expects containerized agent)
- Security vulnerabilities in default configuration

**Required:**
- Implement Docker health checks or `wait-for-it.sh`
- Update `start_node.sh` for Host-Native model
- Generate random security keys on first run

---

### 7. **Security Vulnerabilities** 🔴

**Problem (from full audit):**
- `code_tools.py` uses unchecked `exec()` (RCE risk)
- Audit log currently disabled
- No sandboxing for code execution

**Impact:**
- Malicious code could compromise system
- No audit trail for debugging
- Fails enterprise governance mandate

**Required:**
- Replace `exec()` with containerized execution or secure sandbox
- Enable audit logging
- Implement security boundaries

---

## Bright Spots: Strong Implementations

> [!NOTE]
> Not everything is broken. The full audit identified several **excellent** components that demonstrate high-quality engineering:

### ✅ World-Class Components

1. **`chromadb_context_provider.py`** (Memory Persistence)
   - Perfect MAF SDK compliance
   - Excellent async I/O wrapping
   - Critical project isolation implementation

2. **`project_context.py`** (Multi-Project Foundation)
   - Concurrency-safe using `contextvars`
   - Strict enforcement (RuntimeError on missing context)
   - Clean `@asynccontextmanager` pattern

3. **`universal_tools.py`** (Tool System)
   - Sophisticated framework-agnostic design
   - Built-in PoLA enforcement via roles
   - Advanced schema extraction for LLM reasoning

4. **`governance_agent.py`** (Audit Layer)
   - Textbook async database implementation
   - Perfect separation of concerns
   - Immutability principle enforced

5. **`context_retrieval_agent.py`** (RAG)
   - Clean dependency injection
   - MAF SDK compliant
   - Resolves Phase 10.1 compliance audit

### Key Insight from Full Audit

> **"The project is a strong structural prototype of a MAF architecture, but it fails on critical implementation details necessary for enterprise readiness."**

The audit reveals a **paradox**: The foundation is solid (persistence, context management, tool system), but the execution layer (LLM adapter, delegation, file I/O) is incomplete or broken.

**Metaphor:** "The shape of a car (class hierarchy, interfaces) exists, but the engine and steering wheel (Tool Client, Delegation, Execution) are missing or broken."

---

## Re-Alignment Plan

### Phase 0: Critical Infrastructure Fixes (🔴 BLOCKING)

> [!CAUTION]
> **These issues prevent ANY tool execution.** Must be resolved before workflow orchestration.

Based on comprehensive architecture audit (`feedback/CURRENT.md`), the following technical gaps block all agent functionality:

#### Fix 1: LLM Adapter Tool Call Parsing (🛑 HIGHEST PRIORITY)

**Problem:** `litellm_client.py` cannot parse and execute tool calls from LLM response  
**Impact:** Agents cannot use ANY tools, even if properly defined  
**Root Cause:** Missing tool call extraction and dispatch logic

**Tasks:**
- [ ] Implement tool call parsing in `src/clients/litellm_client.py`
- [ ] Add function call result injection back to LLM
- [ ] Test with simple tool (e.g., `get_time()`)

**Success Criteria:** Agent can successfully invoke and use a basic tool

---

#### Fix 2: Secure File I/O Implementation (🛑 CRITICAL)

**Problem:** `code_tools.py` has no secure file writing tool  
**Impact:** System cannot write code, poses RCE risk  
**Root Cause:** Stubbed implementation

**Tasks:**
- [ ] Create sandboxed `write_file` tool in `src/tools/code_tools.py`
- [ ] Implement path validation (must be within project directory)
- [ ] Add audit logging to PostgreSQL
- [ ] Require approval token from ProjectLead

**Success Criteria:** Can write file with PL approval, rejects unauthorized writes

---

#### Fix 3: Agent Delegation System (⚠️ HIGH PRIORITY)

**Problem:** `communication_tools.py` has `send_message` stub  
**Impact:** ProjectLead cannot delegate to Domain Leads  
**Root Cause:** Incomplete implementation

**Tasks:**
- [ ] Implement `send_message` tool
- [ ] Wire ProjectLead → DomainLead communication
- [ ] Add message routing in agent factory

**Success Criteria:** ProjectLead can send task to DevLead and receive response

---

#### Fix 4: Async I/O Violations (⚠️ MEDIUM PRIORITY)

**Problem:** `liaison_agent.py` and `project_lead_agent.py` use synchronous `os.walk`  
**Impact:** Blocks async event loop during startup  
**Root Cause:** Synchronous file I/O in async context

**Tasks:**
- [ ] Replace `os.walk` with async alternatives or move to background thread
- [ ] Use ContextRetrievalAgent for file tree (already async)
- [ ] Remove direct filesystem access (PoLA violation)

**Success Criteria:** No blocking I/O in agent initialization

---

### Phase 1: Document the Truth (✅ COMPLETED)
- [x] Archive completed infrastructure work
- [x] Create this CURRENT.md to reflect honest reality
- [x] Integrate comprehensive audit findings as Phase 0
- [ ] Update `docs/.ai/agents.md` to add FileWriter Agent spec
- [ ] Update `docs/architecture/CURRENT.md` to reflect current state

---

### Phase 2: Workflow Architecture (BLOCKED BY PHASE 0)

> [!NOTE]
> Cannot proceed until Phase 0 fixes are complete (tools must work first)

#### Milestone 1: FileWriterAgent \u0026 Approval Workflow
**Goal:** Close the loop from code generation to disk write

**Tasks:**
- [ ] Create `src/agents/file_writer_agent.py`
  - Tool: `write_file(path, content, approval_token)`
  - Validation: Requires PL-signed approval token
  - Audit: Logs all writes to PostgreSQL
- [ ] Update ProjectLead to issue approval tokens
- [ ] Create approval workflow test case

**Success Criteria:**
- User says "create README" → Executor generates → DL validates → PL approves → FileWriter writes
- No agent can write without PL approval

#### Milestone 2: Workflow Orchestration Integration
**Goal:** Move from message-passing to workflow execution

**Tasks:**
- [ ] Import MAF SDK `Workflow`, `WorkflowGraph` into ProjectLeadAgent
- [ ] Implement `ProjectLeadAgent.create_workflow(idea: str) -> WorkflowGraph`
- [ ] Parse idea to determine required pillars (Dev? QA? Docs?)
- [ ] Add workflow nodes for each Domain Lead
- [ ] Execute graph and collect results

**Success Criteria:**
- ProjectLead.receive_idea() returns a Workflow execution, not a text response
- Workflow can be paused, checkpointed, and resumed

#### Milestone 3: Domain Lead Orchestration
**Goal:** DLs manage Executor pools, not just validate

**Tasks:**
- [ ] Update `DevLeadAgent` to spawn `CoderAgent` dynamically
- [ ] Implement task queue for Executors
- [ ] Return validated results to ProjectLead

**Success Criteria:**
- DevLead breaks "implement feature X" into 3 CoderAgent tasks
- Each task executes in parallel (if possible)
- Results are validated before returning to PL

#### Milestone 4: PoLA Enforcement
**Goal:** Remove filesystem access from all agents except FileWriter

**Tasks:**
- [ ] Remove `os.walk` and `os.path.exists` from LiaisonAgent
- [ ] Remove filesystem access from ProjectLeadAgent
- [ ] Context injection via ContextRetrievalAgent only
- [ ] Verification test: grep for direct file access

**Success Criteria:**
- Zero direct filesystem imports in Liaison/PL/DL code
- All file reads go through approved Context Retrieval Agent
- All file writes go through FileWriterAgent with approval

---

## Feedback Integration

From `docs/feedback/CURRENT.md`:
- ✅ MAF SDK Compliance is complete (Phase 10.1)
- 🚧 Documentation Architecture redesign is in progress
- ⚠️ No mentioned feedback about agent drift (this is new finding)

**Action:** Once Milestone 1 (FileWriterAgent) is complete, add feedback entry to document the "chatbot drift" issue and resolution.

---

## Dependencies

**Blocks:**
- Full multi-project management (can't scaffold projects without workflow orchestration)
- Enterprise deployment (PoLA violations must be resolved)
- Autonomous agents (need approval workflows, not direct file access)

**Blocked By:**
- None (all infrastructure is in place, this is pure implementation)

**Related:**
- [Vision: Hierarchical MAF Studio](../vision/FUTURE.md#the-hierarchical-maf-studio-ideal-state)
- [Agent Roles](../.ai/agents.md)
- [Architecture: Current State](../architecture/CURRENT.md)
- [Infrastructure Pivot Archive](./ARCHIVE.md#phase-10-multi-project-devstudio---infrastructure-pivot--completed)

---

## Success Metrics

**When This Phase is Complete:**
1. ✅ User can say "build a game" and agents scaffold project structure automatically
2. ✅ All file writes require PL approval (zero rogue writes)
3. ✅ Workflow graphs visible in UI (Live Graph shows orchestration)
4. ✅ Documentation matches reality (no drift between vision and implementation)

**Archive Criteria:**
- All 4 milestones complete
- PoLA verification tests passing
- User can successfully create and run a multi-phase project workflow

---

## Quick Links

- **Vision**: [Hierarchical MAF Studio (FUTURE.md)](../vision/FUTURE.md)
- **Agent Specs**: [agents.md](../.ai/agents.md)
- **Architecture**: [CURRENT.md](../architecture/CURRENT.md)
- **Completed Work**: [ARCHIVE.md](./ARCHIVE.md)
- **Feedback**: [feedback/CURRENT.md](../feedback/CURRENT.md)
