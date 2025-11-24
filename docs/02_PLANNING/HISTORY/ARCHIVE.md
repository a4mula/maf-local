# Planning Archive

---

## Emergency Refactor: Weeks 1-4 ✅ COMPLETED

**Duration:** 4 weeks (November 2025)  
**Goal:** Fix broken execution layer and establish working MVP before rebuilding complexity  
**Trigger:** Expert Systems Assessment identified "Architecture Astronaut Trap"

### Context

Following Phase 10 Infrastructure Pivot, comprehensive audit revealed critical execution layer failures:
- `litellm_client.py` couldn't parse tool calls from LLMs
- No secure file writing capability
- Complex agent hierarchy with no working implementation
- "Beautiful architecture with no engine"

### Strategic Decision: MVP-First Refactor

Paused all feature development to:
1. Fix core mechanics (tool execution, file I/O)
2. Simplify architecture (delete unused agents)
3. Prove one working flow
4. Rebuild incrementally with tests

### Weekly Deliverables

**Week 1: Emergency Fixes** ✅
- Fixed `litellm_client.py` tool calling (proper JSON parsing)
- Implemented sandboxed `write_file` tool with path validation
- Wired end-to-end flow (User → Agent → Tool → Response)
- Created integration tests

**Week 2: Simplification** ✅
- Deleted unused agents: DomainLead, Executor, Governance, ContextRetrieval, ArtifactManager
- Kept only Liaison + ProjectLead
- Verified message passing works
- Updated AgentFactory for 2-tier architecture

**Week 3: File Generation MVP** ✅
- Verified working flow: User → Liaison → ProjectLead → write_file → Disk
- Real agent created `demo.txt` successfully
- Integration tests confirm E2E functionality

**Week 4: MAF-Compliant Client** ✅
- Refactored `LiteLLMChatClient` to extend `BaseChatClient`
- Applied `@use_function_invocation` decorator for automatic tool execution
- Converted tools to `AIFunction` objects using `ai_function()`
- Deleted custom `CoreAgent` (MAF handles loop natively)
- All integration tests pass

### Technical Improvements

- ✅ **MAF SDK Compliance:** Client properly implements `ChatClientProtocol`
- ✅ **Automatic Tool Execution:** Framework handles the execution loop
- ✅ **Simplified Architecture:** 2-tier hierarchy proven functional
- ✅ **Test Coverage:** Integration tests verify structure and flow
- ✅ **File Generation:** Agents can create files on disk securely

### Files Modified

**Deleted:**
- `src/agents/core_agent.py`
- `src/agents/domain_lead_agent.py`
- `src/agents/executor_agent.py`
- `src/agents/governance_agent.py`
- `src/agents/context_retrieval_agent.py`
- `src/agents/artifact_manager_agent.py`
- `tests/integration/test_end_to_end_flow.py`

**Created:**
- `src/api_server.py`
- `tests/integration/test_factory_startup.py`
- `tests/integration/test_message_passing.py`
- `tests/integration/test_file_generation_flow.py`
- `tests/unit/test_litellm_tool_parsing.py`
- `tests/unit/test_secure_file_io.py`

**Refactored:**
- `src/clients/litellm_client.py` - Extended `BaseChatClient`, added decorator
- `src/agents/project_lead_agent.py` - Uses standard `ChatAgent`
- `src/services/agent_factory.py` - Simplified dependencies
- `src/tools/universal_tools.py` - Added `get_ai_functions()`

### Verification

- ✅ All 3 integration tests pass
- ✅ File generation confirmed (real agent created demo.txt)
- ✅ Tool execution working through MAF decorator
- ✅ No custom execution loops required

### Outcome

**Technical Achievement:** Working MVP with MAF-compliant tool execution  
**Architectural Improvement:** Eliminated "architecture astronaut" complexity  
**Unblocks:** Can now rebuild multi-tier hierarchy incrementally with confidence

**Key Learning:** "Prove minimal system works, then scale with tests at each step"

---

## Phase 10: Multi-Project DevStudio - Infrastructure Pivot ✅ COMPLETED

**Duration:** 1 day (2025-11-22)  
**Goal:** Pivot from containerized application to host-native runtime + establish multi-project foundation  
**Trigger:** Docker friction, permission issues, path mapping complexity

### Context

The original Phase 10 Milestone 1 was partially completed (database schema), but revealed fundamental architectural issues:
- Docker volume mounting created permission hell (UID/GID mismatches)
- Path confusion (`/workspaces` in container vs `/home/robb/projects` on host)
- Agent GUI and API needed restart to mount new project folders
- Violated "IDE-like" UX expectations

### Strategic Decision: Host-Native Runtime

Following architectural review comparison to VS Code and Antigravity, pivoted to:
- **Infrastructure in Docker**: PostgreSQL, Ollama, ChromaDB, LiteLLM (hard to install, benefit from isolation)
- **Application on Host**: Agent API and Streamlit UI run natively (Python venv)
- **Direct File Access**: No volume mount complexity, native permissions

### Key Deliverables

1. **Host-Native Startup Script** ([`run_studio.sh`](file:///home/robb/projects/maf-local/run_studio.sh))
   - Creates/activates Python `.venv`
   - Installs `requirements.txt`
   - Sets environment variables (localhost URLs)
   - Launches Agent API (background) + Streamlit UI (foreground)

2. **Docker Compose Refactor** ([`docker-compose.yaml`](file:///home/robb/projects/maf-local/docker-compose.yaml))
   - Removed `maf-ui` and `maf-agent` services
   - Exposed ports: PostgreSQL (5432), Ollama (11434), ChromaDB (8000), LiteLLM (4000)
   - Infrastructure-only (6 services)

3. **Database Schema Completion**
   - Created `governance_decisions` table (with `category` column per code expectations)
   - Created `workflow_checkpoints` table (proper schema)
   - Created `projects` table (with `path` column, not `workspace_path`)
   - Ran migrations: `2025_11_20_governance.sql`, `2025_11_20_checkpoints.sql`, `2025_11_21_phase_10_multi_project.sql`

4. **UI Redesign** ([`src/ui/streamlit_app.py`](file:///home/robb/projects/maf-local/src/ui/streamlit_app.py))
   - Project dropdown with "➕ New Project..." option
   - Collapsible file tree using `streamlit-tree-select`
   - Project creation auto-generates sibling paths (`../MyNewApp`)
   - Fixed `project_id` vs `id` key mismatches throughout

5. **Project Service** ([`src/services/project_service.py`](file:///home/robb/projects/maf-local/src/services/project_service.py))
   - Auto-creates project directories (`os.makedirs`)
   - Stores projects in PostgreSQL
   - Path validation and normalization

### Technical Improvements

- ✅ **Zero Permission Issues**: Agent runs as host user
- ✅ **Native Paths**: `/home/robb/projects/MyProject` (no translation layer)
- ✅ **No Container Restart**: Create projects without rebuilding
- ✅ **IDE-like UX**: File explorer shows real host files
- ✅ **Dependency Management**: `requirements.txt` + `streamlit-tree-select`

### Verification

- ✅ Project creation works (`/home/robb/projects/Test` created successfully)
- ✅ Database schema complete (all migrations applied)
- ✅ Agent responds without errors (governance tables exist)
- ✅ UI File Explorer displays project structure

### Known Limitations (Deferred to Next Phase)

- ⚠️ **Agents are Chatbots**: LiaisonAgent and ProjectLeadAgent pass messages, not workflows
- ⚠️ **No Workflow Orchestration**: MAF Workflow Graph not integrated
- ⚠️ **No Domain Leads**: Classes exist but not instantiated or wired
- ⚠️ **No Executors**: Task execution layer missing
- ⚠️ **PoLA Violation**: Liaison/PL access filesystem directly (should be read-only)

---

## Phase 10.1: MAF SDK Compliance Refactoring ✅ COMPLETED



**Duration:** 3 hours (2025-11-21)  
**Goal:** Refactor memory persistence to comply with MAF SDK Context Provider pattern  
**Trigger:** MAF SDK Compliance Audit identified architectural violation

### Context

MAF SDK Compliance Audit revealed that `ContextRetrievalAgent` directly instantiated `chromadb.HttpClient`, bypassing MAF SDK's Context Provider interface. This violated enterprise governance requirements and blocked Phase 10 implementation.

**Compliance Score Before:** 🟡 70% (5 of 6 areas compliant)  
**Compliance Score After:** 🟢 100% (6 of 6 areas compliant)

### Key Deliverable

**ChromaDB Context Provider** - MAF SDK-compliant memory persistence layer

**Implementation:**
1. Created [`src/persistence/chromadb_context_provider.py`](file:///home/robb/projects/maf-local/src/persistence/chromadb_context_provider.py)
   - Implements Context Provider interface
   - Async methods: `store()`, `query()`, `retrieve()`, `delete()`
   - Full type hints and error handling
   - Enterprise governance integration ready

2. Refactored [`src/agents/context_retrieval_agent.py`](file:///home/robb/projects/maf-local/src/agents/context_retrieval_agent.py)
   - Accepts `ChromaDBContextProvider` via dependency injection
   - Removed direct database access
   - Backward-compatible public API

3. Updated [`src/services/agent_factory.py`](file:///home/robb/projects/maf-local/src/services/agent_factory.py)
   - Instantiates provider at startup
   - Injects into agent constructor

### Tests Created

- `tests/unit/test_chromadb_context_provider.py` - Provider unit tests
- `tests/integration/test_context_retrieval_agent.py` - Agent integration tests

### Verification

- ✅ Zero direct database access in agent code (grep verified)
- ✅ All persistence layers use MAF SDK interfaces
- ✅ Dependency injection pattern implemented
- ✅ Comprehensive test coverage
- ✅ Documentation updated

### Outcome

**Technical Achievement:** Full MAF SDK compliance (100%)  
**Architectural Improvement:** Dependency injection enables testability and enterprise governance  
**Unblocks:** Phase 10 (Multi-Project DevStudio) can now proceed

**Files Modified:**
- `src/persistence/chromadb_context_provider.py` (NEW)
- `src/agents/context_retrieval_agent.py` (REFACTORED)
- `src/services/agent_factory.py` (UPDATED)
- `docs/architecture/CURRENT.md` (DOCUMENTED)
- `docs/feedback/CURRENT.md` (MARKED RESOLVED)

---

## Phase 10.0: Documentation Architecture Redesign ✅ COMPLETED


**Duration:** 1 day (2025-11-21)  
**Goal:** Establish consistent, agent-first documentation structure using CURRENT + ARCHIVE pattern universally

### Context

After 9 phases of development, documentation had grown organically across 16 files and 9 directories with inconsistent patterns. This phase aimed to refactor the entire documentation system for agent-driven workflows.

### Key Deliverables

1. **Consolidated `.ai/` folder** (7 files → 3 files):
   - `MANIFEST.yaml` - Feature tracking + navigation shortcuts + update templates
   - `GUIDELINES.md` - Coding standards + MAF SDK compliance rules
   - `agents.md` - Agent roles, tools, and boundaries

2. **Applied CURRENT + ARCHIVE pattern**:
   - `planning/` - CURRENT.md (active phase) + ARCHIVE.md (historical) + WORKFLOW.md (meta)
   - `feedback/` - CURRENT.md (active issues) + ARCHIVE.md (resolved)
   - `architecture/` - CURRENT.md (system state) + DECISIONS.md (ADRs)

3. **Merged redundant directories**:
   - `tutorials/` + `how-to/` → `guides/` (task-oriented docs)
   - `explanation/` → `why/RATIONALE.md` (design rationale)
   - `vision/` → `FUTURE.md` (roadmap)

4. **Created navigation layer**:
   - `docs/INDEX.md` - Master documentation index
   - `research/INDEX.md` - Research catalog
   - `README.md` updated with human/agent entry points

5. **Added YAML frontmatter** to all docs with:
   - `access:` - Permission levels (read-only, read-write, restricted)
   - `audience:` - Target readers (agents, humans, all)
   - `update_trigger:` - When to update
   - `managed_by:` - Who maintains

### Files Created

- `/docs/.ai/MANIFEST.yaml`
- `/docs/.ai/GUIDELINES.md`
- `/docs/feedback/CURRENT.md`
- `/docs/feedback/ARCHIVE.md`
- `/docs/architecture/DECISIONS.md`
- `/docs/vision/FUTURE.md`
- `/docs/why/RATIONALE.md`
- `/docs/research/INDEX.md`
- `/docs/INDEX.md`
- `/docs/planning/implementations/documentation_architecture_redesign.md`
- `/docs/feedback/documentation_system_audit.md`

### Files Renamed

- `architecture/CURRENT_STATE.md` → `architecture/CURRENT.md`
- `planning/CURRENT_PHASE.md` → `planning/CURRENT.md`
- `planning/Phase_Planner_ARCHIVE.md` → `planning/ARCHIVE.md`
- `planning/phase_management_workflow.md` → `planning/WORKFLOW.md`

### Files Removed

- `.ai/feature_manifest.yaml` (merged into MANIFEST.yaml)
- `.ai/update_templates.yaml` (merged into MANIFEST.yaml)
- `.ai/project_guidelines.md` (merged into GUIDELINES.md)
- `.ai/AGENT_INSTRUCTIONS.md` (merged into GUIDELINES.md)
- `.ai/copilot-instructions.md` (obsolete)
- `.ai/update_guidelines.md` (obsolete)
- `feedback/maf-local_feedback_v2.md` (consolidated)
- `feedback/maf_sdk_compliance_audit.md` (moved to CURRENT.md)
- `feedback/documentation_architecture_redesign_status.md` (consolidated)
- `vision/ideal_state.md` (consolidated into FUTURE.md)
- `planning/roadmap.md` (content in ARCHIVE.md)
- Entire `tutorials/`, `how-to/`, `explanation/` directories

### Outcome

**Before:** 16 files, 9 directories, inconsistent patterns, unclear agent access  
**After:** 18 files (structured), 7 directories, universal CURRENT + ARCHIVE pattern, clear entry points

**Benefits:**
- ✅ Clear human/agent entry points from README.md
- ✅ Consistent temporal pattern across all documentation
- ✅ Permission levels documented in YAML frontmatter
- ✅ Navigation shortcuts in MANIFEST.yaml
- ✅ Reduced redundancy (7 files deleted)
- ✅ Diataxis-aligned structure (learning, task, reference, understanding)

**Remaining Gaps** (identified in audit):
- ⚠️ DocUpdatePlanner tool not implemented (templates exist, no code)
- ⚠️ Permission enforcement not automated (YAML rules not enforced)
- ⚠️ No MAF SDK integration (governance, checkpointing, auditing)
- ⚠️ No Git versioning strategy for docs

**Decision:** Defer documentation automation to Phase 11. Foundation is solid; prove patterns manually first.

---

Phase\_Planner.md

## **1️⃣ Phase 1 – Agent Hierarchy (Weeks 1‑2)**

| Deliverable | File | What it contains |
| :---- | :---- | :---- |
| Liaison Agent | src/agents/liaison\_agent.py | Minimal ChatAgent that only captures user intent and forwards the raw idea to the Project Lead. No tools are exposed. |
| Project Lead Agent | src/agents/project\_lead\_agent.py | Central decision‑maker. Holds the workflow‑creation logic, delegates to Domain Leads, and writes authoritative decisions to the Governance Agent. |
| Domain Lead Agents | src/agents/domain\_lead\_agent.py | One class that can be instantiated per pillar (development, qa, documentation). It injects pillar‑specific context and assigns tasks to Executors. |
| Executor Agents | src/agents/executor\_agent.py | Very thin wrappers around the universal tool registry. Each executor receives a single, atomic task and escalates any ambiguity. |
| Agent Registry | src/agents/\_\_init\_\_.py | Exposes the four agent classes for the factory. |

### Sample skeletons

python  
\# src/agents/liaison\_agent.py  
from agent\_framework import ChatAgent

class LiaisonAgent:  
   """Tier 1 – UI front‑end. Captures intent, asks clarifying questions,  
   then forwards the final idea to the Project Lead."""  
   def \_\_init\_\_(self, project\_lead):  
       self.project\_lead \= project\_lead  
       self.sdk\_agent \= ChatAgent(  
           name\="Liaison",  
           instructions\=(  
               "Capture the user's raw idea. "  
               "Ask only clarifying questions. "  
               "Never make technical decisions."  
           ),  
           tools\=\[\],  
       )

   async def handle(self, user\_msg):  
       \# Forward the final idea to PL  
       await self.project\_lead.receive\_idea(user\_msg)  
python  
\# src/agents/project\_lead\_agent.py  
from agent\_framework import ChatAgent  
from src.agents.governance\_agent import GovernanceAgent  
from src.tools.universal\_tools import registry

class ProjectLeadAgent:  
   """Tier 2 – Sole technical decision‑maker."""  
   def \_\_init\_\_(self, governance: GovernanceAgent):  
       self.governance \= governance  
       self.sdk\_agent \= ChatAgent(  
           name\="ProjectLead",  
           instructions\=(  
               "Create a structured, non‑boilerplate plan. "  
               "Translate the plan into a MAF Workflow graph. "  
               "Delegate sub‑graphs to Domain Leads. "  
               "Persist every decision via GovernanceAgent."  
           ),  
           tools\=\[  
               registry.get\_tool("create\_workflow"),  
               registry.get\_tool("delegate\_to\_dl"),  
               registry.get\_tool("update\_governance"),  
           \],  
       )

   async def receive\_idea(self, idea\_msg):  
       \# Kick‑off planning – ask the Liaison for clarification if needed  
       \# (implementation left to the ChatAgent loop)  
       pass

   async def store\_decision(self, decision):  
       await self.governance.store\_decision(decision)  
python  
\# src/agents/domain\_lead\_agent.py  
from agent\_framework import ChatAgent  
from src.agents.context\_retrieval\_agent import ContextRetrievalAgent

class DomainLeadAgent:  
   """Tier 3 – Pillar manager (Dev / QA / Docs)."""  
   def \_\_init\_\_(self, pillar: str, context\_agent: ContextRetrievalAgent):  
       self.pillar \= pillar  
       self.context\_agent \= context\_agent  
       self.sdk\_agent \= ChatAgent(  
           name\=f"DomainLead\_{pillar}",  
           instructions\=(  
               f"Manage {pillar} executors. "  
               "Filter context through the ContextRetrievalAgent. "  
               "Escalate any ambiguity to the Project Lead."  
           ),  
           tools\=\[  
               registry.get\_tool("assign\_task"),  
               registry.get\_tool("retrieve\_context"),  
               registry.get\_tool("escalate"),  
           \],  
       )  
python  
\# src/agents/executor\_agent.py  
from agent\_framework import ChatAgent  
from src.tools.universal\_tools import registry

class ExecutorAgent:  
   """Tier 4 – Atomic worker (Coder, Tester, Writer)."""  
   def \_\_init\_\_(self, role: str):  
       self.role \= role  
       self.sdk\_agent \= ChatAgent(  
           name\=f"Executor\_{role}",  
           instructions\=(  
               f"Perform a single atomic {role.lower()} task. "  
               "Never assume missing information – immediately call \`escalate\`."  
           ),  
           tools\=registry.get\_tools\_for\_role(role),  
       )

### Immediate actions

1. Create the four files above (use write\_to\_file if you want me to generate them now).  
2. Add imports in src/agents/\_\_init\_\_.py so the factory can instantiate them.  
3. Update   
4. src/services/agent\_factory.py to build the hierarchy:  
5. python  
6. liaison \= LiaisonAgent(project\_lead)  
   project\_lead \= ProjectLeadAgent(governance)  
   dev\_dl \= DomainLeadAgent("development", context\_agent)  
   qa\_dl \= DomainLeadAgent("qa", context\_agent)  
   exec\_coder \= ExecutorAgent("Coder")  
   exec\_tester \= ExecutorAgent("Tester")  
   \# Wire them together via MessageBus

---

## **2️⃣ Phase 2 – Governance Layer (Weeks 3‑4)**

| Deliverable | File | Description |
| :---- | :---- | :---- |
| Governance Agent | src/agents/governance\_agent.py | Stores immutable decisions (YAML/JSON) in PostgreSQL, provides drift‑detection API. |
| DB migration | src/persistence/migrations/2025\_11\_20\_governance.sql | Creates governance\_decisions and drift\_log tables (see plan). |
| Drift detection utility | src/services/drift\_detection.py | Compares current system state with stored decisions; returns a list of mismatches. |
| Decision model | src/models/decision.py | Pydantic model with to\_yaml() helper. |

### Quick code sketch for the agent

python  
\# src/agents/governance\_agent.py  
import json  
from datetime import datetime  
from uuid import uuid4  
from src.persistence.postgres import PostgresClient  
from src.models.decision import Decision

class GovernanceAgent:  
   def \_\_init\_\_(self, db: PostgresClient):  
       self.db \= db

   async def store\_decision(self, decision: Decision):  
       await self.db.execute(  
           """  
           INSERT INTO governance\_decisions  
               (decision\_id, category, content, created\_at, created\_by, immutable)  
           VALUES ($1, $2, $3, $4, $5, true)  
           """,  
           uuid4(),  
           decision.category,  
           json.dumps(decision.content),  
           datetime.utcnow(),  
           "ProjectLead",  
       )

   async def get\_all\_decisions(self):  
       rows \= await self.db.fetch("SELECT \* FROM governance\_decisions")  
       return \[Decision(\*\*row) for row in rows\]

   async def check\_drift(self, current\_state):  
       decisions \= await self.get\_all\_decisions()  
       \# \`detect\_drift\` is a pure‑function utility  
       return detect\_drift(decisions, current\_state)  
Next steps

1. Add the migration file and run it (docker exec maf-postgres psql \-U maf \-d maf \-f /migrations/...).  
2. Implement detect\_drift (simple diff of stored YAML vs generated state).  
3. Wire the GovernanceAgent into the ProjectLeadAgent (see Phase 1 skeleton).

---

## **3️⃣ Phase 3 – Workflow Checkpointing (Weeks 5‑6)**

| Deliverable | File | Purpose |
| :---- | :---- | :---- |
| Checkpoint storage | src/persistence/checkpoint\_storage.py | Implements CheckpointStorage using PostgreSQL (workflow\_checkpoints table). |
| MAF workflow class | src/workflows/maf\_workflow.py | Uses with\_checkpointing() and defines plan → implement → test steps. |
| DB migration | src/persistence/migrations/2025\_11\_20\_checkpoints.sql | Creates workflow\_checkpoints table. |

### Minimal migration

sql  
CREATE TABLE workflow\_checkpoints (  
   checkpoint\_id UUID PRIMARY KEY,  
   workflow\_id VARCHAR(100),  
   state BYTEA,          \-- Serialized MAF WorkflowState  
   created\_at TIMESTAMP  
);  
Immediate actions

1. Add the migration file and apply it.  
2. Implement PostgreSQLCheckpointStorage.save\_checkpoint / load\_checkpoint (already sketched in the plan).  
3. Refactor   
4. src/workflows/main\_orchestrator.py to subclass Workflow and call await self.with\_checkpointing().

---

## **4️⃣ Phase 4 – Context Management (Weeks 7‑8)**

| Deliverable | File | What it does |
| :---- | :---- | :---- |
| Context Retrieval Agent | src/agents/context\_retrieval\_agent.py | Queries ChromaDB (fast RAG) and pgvector (governance docs), returns a filtered Context object. |
| Chroma wrapper | src/persistence/chroma\_store.py | Simple async wrapper around chromadb.HttpClient. |
| Vector search helper | src/services/pg\_vector\_search.py | Executes SELECT \* FROM vectors WHERE embedding \<=\> query LIMIT n. |
| Context model | src/models/context.py | Pydantic model with embeddings and governance fields. |

Key integration point – Domain Leads call 

ContextRetrievalAgent.get\_relevant\_context(query, pillar) before assigning a task to an Executor. This guarantees that each Executor receives only the minimal, pillar‑specific knowledge it needs.  
Next steps

1. Add the two wrapper classes (chroma\_store.py, pg\_vector\_search.py).  
2. Create ContextRetrievalAgent with the async methods shown in the plan.  
3. Update DomainLeadAgent to call self.context\_agent.get\_relevant\_context(...) before assign\_task.

---

## **5️⃣ Phase 5 – Artifact Management (Weeks 9‑10)**

| Deliverable | File | Role |
| :---- | :---- | :---- |
| Artifact Manager Agent | src/agents/artifact\_manager\_agent.py | Sole authority for file reads/writes and Git commits. |
| Restricted code\_tools.py | src/tools/code\_tools.py | Decorated with @require\_role("ArtifactManager"). |
| Git helper | src/services/git\_helper.py | Simple wrapper around gitpython (or subprocess) to commit changes. |

Why this matters – All code‑generation or file‑modification tools now go through a single, auditable gate. The 

ArtifactManagerAgent can log every change, run staticBelow is the next‑level detail that expands the high‑level phases from the implementation plan you just added.  
I’ve broken each phase into concrete deliverables, file skeletons, and the immediate actions you can take to keep the project moving forward.  
---

## **1️⃣ Phase 1 – Agent Hierarchy (Weeks 1‑2)**

| Deliverable | File | What it contains |
| :---- | :---- | :---- |
| Liaison Agent | src/agents/liaison\_agent.py | Minimal ChatAgent that only captures user intent and forwards the raw idea to the Project Lead. No tools are exposed. |
| Project Lead Agent | src/agents/project\_lead\_agent.py | Central decision‑maker. Holds the workflow‑creation logic, delegates to Domain Leads, and writes authoritative decisions to the Governance Agent. |
| Domain Lead Agents | src/agents/domain\_lead\_agent.py | One class that can be instantiated per pillar (development, qa, documentation). It injects pillar‑specific context and assigns tasks to Executors. |
| Executor Agents | src/agents/executor\_agent.py | Very thin wrappers around the universal tool registry. Each executor receives a single, atomic task and escalates any ambiguity. |
| Agent Registry | src/agents/\_\_init\_\_.py | Exposes the four agent classes for the factory. |

### Sample skeletons

python  
\# src/agents/liaison\_agent.py  
from agent\_framework import ChatAgent

class LiaisonAgent:  
   """Tier 1 – UI front‑end. Captures intent, asks clarifying questions,  
   then forwards the final idea to the Project Lead."""  
   def \_\_init\_\_(self, project\_lead):  
       self.project\_lead \= project\_lead  
       self.sdk\_agent \= ChatAgent(  
           name\="Liaison",  
           instructions\=(  
               "Capture the user's raw idea. "  
               "Ask only clarifying questions. "  
               "Never make technical decisions."  
           ),  
           tools\=\[\],  
       )

   async def handle(self, user\_msg):  
       \# Forward the final idea to PL  
       await self.project\_lead.receive\_idea(user\_msg)  
python  
\# src/agents/project\_lead\_agent.py  
from agent\_framework import ChatAgent  
from src.agents.governance\_agent import GovernanceAgent  
from src.tools.universal\_tools import registry

class ProjectLeadAgent:  
   """Tier 2 – Sole technical decision‑maker."""  
   def \_\_init\_\_(self, governance: GovernanceAgent):  
       self.governance \= governance  
       self.sdk\_agent \= ChatAgent(  
           name\="ProjectLead",  
           instructions\=(  
               "Create a structured, non‑boilerplate plan. "  
               "Translate the plan into a MAF Workflow graph. "  
               "Delegate sub‑graphs to Domain Leads. "  
               "Persist every decision via GovernanceAgent."  
           ),  
           tools\=\[  
               registry.get\_tool("create\_workflow"),  
               registry.get\_tool("delegate\_to\_dl"),  
               registry.get\_tool("update\_governance"),  
           \],  
       )

   async def receive\_idea(self, idea\_msg):  
       \# Kick‑off planning – ask the Liaison for clarification if needed  
       \# (implementation left to the ChatAgent loop)  
       pass

   async def store\_decision(self, decision):  
       await self.governance.store\_decision(decision)  
python  
\# src/agents/domain\_lead\_agent.py  
from agent\_framework import ChatAgent  
from src.agents.context\_retrieval\_agent import ContextRetrievalAgent

class DomainLeadAgent:  
   """Tier 3 – Pillar manager (Dev / QA / Docs)."""  
   def \_\_init\_\_(self, pillar: str, context\_agent: ContextRetrievalAgent):  
       self.pillar \= pillar  
       self.context\_agent \= context\_agent  
       self.sdk\_agent \= ChatAgent(  
           name\=f"DomainLead\_{pillar}",  
           instructions\=(  
               f"Manage {pillar} executors. "  
               "Filter context through the ContextRetrievalAgent. "  
               "Escalate any ambiguity to the Project Lead."  
           ),  
           tools\=\[  
               registry.get\_tool("assign\_task"),  
               registry.get\_tool("retrieve\_context"),  
               registry.get\_tool("escalate"),  
           \],  
       )  
python  
\# src/agents/executor\_agent.py  
from agent\_framework import ChatAgent  
from src.tools.universal\_tools import registry

class ExecutorAgent:  
   """Tier 4 – Atomic worker (Coder, Tester, Writer)."""  
   def \_\_init\_\_(self, role: str):  
       self.role \= role  
       self.sdk\_agent \= ChatAgent(  
           name\=f"Executor\_{role}",  
           instructions\=(  
               f"Perform a single atomic {role.lower()} task. "  
               "Never assume missing information – immediately call \`escalate\`."  
           ),  
           tools\=registry.get\_tools\_for\_role(role),  
       )

### Immediate actions

1. Create the four files above (use write\_to\_file if you want me to generate them now).  
2. Add imports in src/agents/\_\_init\_\_.py so the factory can instantiate them.  
3. Update   
4. src/services/agent\_factory.py to build the hierarchy:  
5. python  
6. liaison \= LiaisonAgent(project\_lead)  
   project\_lead \= ProjectLeadAgent(governance)  
   dev\_dl \= DomainLeadAgent("development", context\_agent)  
   qa\_dl \= DomainLeadAgent("qa", context\_agent)  
   exec\_coder \= ExecutorAgent("Coder")  
   exec\_tester \= ExecutorAgent("Tester")  
   \# Wire them together via MessageBus

---

## **2️⃣ Phase 2 – Governance Layer (Weeks 3‑4)**

| Deliverable | File | Description |
| :---- | :---- | :---- |
| Governance Agent | src/agents/governance\_agent.py | Stores immutable decisions (YAML/JSON) in PostgreSQL, provides drift‑detection API. |
| DB migration | src/persistence/migrations/2025\_11\_20\_governance.sql | Creates governance\_decisions and drift\_log tables (see plan). |
| Drift detection utility | src/services/drift\_detection.py | Compares current system state with stored decisions; returns a list of mismatches. |
| Decision model | src/models/decision.py | Pydantic model with to\_yaml() helper. |

### Quick code sketch for the agent

python  
\# src/agents/governance\_agent.py  
import json  
from datetime import datetime  
from uuid import uuid4  
from src.persistence.postgres import PostgresClient  
from src.models.decision import Decision

class GovernanceAgent:  
   def \_\_init\_\_(self, db: PostgresClient):  
       self.db \= db

   async def store\_decision(self, decision: Decision):  
       await self.db.execute(  
           """  
           INSERT INTO governance\_decisions  
               (decision\_id, category, content, created\_at, created\_by, immutable)  
           VALUES ($1, $2, $3, $4, $5, true)  
           """,  
           uuid4(),  
           decision.category,  
           json.dumps(decision.content),  
           datetime.utcnow(),  
           "ProjectLead",  
       )

   async def get\_all\_decisions(self):  
       rows \= await self.db.fetch("SELECT \* FROM governance\_decisions")  
       return \[Decision(\*\*row) for row in rows\]

   async def check\_drift(self, current\_state):  
       decisions \= await self.get\_all\_decisions()  
       \# \`detect\_drift\` is a pure‑function utility  
       return detect\_drift(decisions, current\_state)  
Next steps

1. Add the migration file and run it (docker exec maf-postgres psql \-U maf \-d maf \-f /migrations/...).  
2. Implement detect\_drift (simple diff of stored YAML vs generated state).  
3. Wire the GovernanceAgent into the ProjectLeadAgent (see Phase 1 skeleton).

---

## **3️⃣ Phase 3 – Workflow Checkpointing (Weeks 5‑6)**

| Deliverable | File | Purpose |
| :---- | :---- | :---- |
| Checkpoint storage | src/persistence/checkpoint\_storage.py | Implements CheckpointStorage using PostgreSQL (workflow\_checkpoints table). |
| MAF workflow class | src/workflows/maf\_workflow.py | Uses with\_checkpointing() and defines plan → implement → test steps. |
| DB migration | src/persistence/migrations/2025\_11\_20\_checkpoints.sql | Creates workflow\_checkpoints table. |

### Minimal migration

sql  
CREATE TABLE workflow\_checkpoints (  
   checkpoint\_id UUID PRIMARY KEY,  
   workflow\_id VARCHAR(100),  
   state BYTEA,          \-- Serialized MAF WorkflowState  
   created\_at TIMESTAMP  
);  
Immediate actions

1. Add the migration file and apply it.  
2. Implement PostgreSQLCheckpointStorage.save\_checkpoint / load\_checkpoint (already sketched in the plan).  
3. Refactor   
4. src/workflows/main\_orchestrator.py to subclass Workflow and call await self.with\_checkpointing().

---

## **4️⃣ Phase 4 – Context Management (Weeks 7‑8)**

| Deliverable | File | What it does |
| :---- | :---- | :---- |
| Context Retrieval Agent | src/agents/context\_retrieval\_agent.py | Queries ChromaDB (fast RAG) and pgvector (governance docs), returns a filtered Context object. |
| Chroma wrapper | src/persistence/chroma\_store.py | Simple async wrapper around chromadb.HttpClient. |
| Vector search helper | src/services/pg\_vector\_search.py | Executes SELECT \* FROM vectors WHERE embedding \<=\> query LIMIT n. |
| Context model | src/models/context.py | Pydantic model with embeddings and governance fields. |

Key integration point – Domain Leads call 

ContextRetrievalAgent.get\_relevant\_context(query, pillar) before assigning a task to an Executor. This guarantees that each Executor receives only the minimal, pillar‑specific knowledge it needs.  
Next steps

1. Add the two wrapper classes (chroma\_store.py, pg\_vector\_search.py).  
2. Create ContextRetrievalAgent with the async methods shown in the plan.  
3. Update DomainLeadAgent to call self.context\_agent.get\_relevant\_context(...) before assign\_task.

---

## **5️⃣ Phase 5 – Artifact Management (Weeks 9‑10)**

| Deliverable | File | Role |
| :---- | :---- | :---- |
| Artifact Manager Agent | src/agents/artifact\_manager\_agent.py | Sole authority for file reads/writes and Git commits. |
| Restricted code\_tools.py | src/tools/code\_tools.py | Decorated with @require\_role("ArtifactManager"). |
| Git helper | src/services/git\_helper.py | Simple wrapper around gitpython (or subprocess) to commit changes. |

Why this matters – All code‑generation or file‑modification tools now go through a single, auditable gate. The 

ArtifactManagerAgent can log every change, run static analysis, and enforce PR‑style reviews if desired.  
Immediate actions

1. Scaffold artifact\_manager\_agent.py (see plan).  
2. Add the require\_role decorator (aa tiny wrapper that checks the calling agent’s name).  
3. Update code\_tools.py to use the decorator and raise an error if called from any other agent.

---

## **6️⃣ Phase 6 – Provider Discovery & Intelligent Routing (Weeks 11‑12)**

| Deliverable | File | Function |
| :---- | :---- | :---- |
| Provider Discovery Service | src/services/provider\_discovery.py | Reads API keys, queries each provider’s model‑list endpoint, stores capabilities in the Governance DB. |
| Intelligent Router | src/services/intelligent\_router.py | Picks the best model for a given task based on capability, cost, rate‑limit, and FOSS‑first policy. |
| Governance tables | src/persistence/migrations/2025\_11\_20\_providers.sql | providers, models, capabilities tables. |
| Model capability schema | src/models/model\_info.py | Pydantic model with  name, cost, capabilities, rate\_limit. |

Workflow

1. On startup, ProviderDiscoveryService.discover\_from\_keys() runs once (or on a schedule).  
2. The IntelligentRouter.select\_for\_task(task\_type, max\_cost, min\_speed) is called by the ProjectLeadAgent whenever a new tool call needs a model.  
3. The router returns the *model alias* that the LiteLLM client will use (e.g., "maf-ollama/llama3.1" or a free‑tier Groq model).

Next steps

1. Add the migration for provider tables.  
2. Implement a simple HTTP call to each provider’s /v1/models (or equivalent) using httpx.  
3. Wire the router into ProjectLeadAgent – replace any hard‑coded model\_name usage with await router.select\_for\_task(...).

---

## **7️⃣ Phase 7 – Observability Layer (Weeks 13‑14) (COMPLETED)**

| Deliverable | File | Function |
| :---- | :---- | :---- |
| Prometheus Config | config/prometheus.yml | Scrapes metrics from the agent container. |
| Grafana Dashboard | (UI) | Visualizes system health, token usage, and agent activity. |
| Metrics Endpoint | src/services/metrics_service.py | Exposes custom metrics (agent_state, tool_usage) for Prometheus. |

**Status:** ✅ **DONE**. Prometheus and Grafana are running in Docker. Agents expose metrics on port 8002.

---

## **8️⃣ Phase 8 – Bootstrap User Interface (Weeks 15‑16) (COMPLETED)**

| Deliverable | File | Function |
| :---- | :---- | :---- |
| Streamlit App | src/ui/streamlit_app.py | Provides chat interface and system status. |
| Live Agent Graph | ui-next/ | Next.js application rendering real-time agent hierarchy and status. |
| API Endpoints | src/api/agent_api.py | Serves agent status and handles chat messages. |

**Status:** ✅ **DONE**. Streamlit runs on port 8501. Next.js Graph runs on port 3000. Both are integrated.

---

## **9️⃣ Phase 9 – Self-Contained Node Formalization (Weeks 17‑18) (COMPLETED)**

| Deliverable | File | Function |
| :---- | :---- | :---- |
| Dockerfiles | docker/Dockerfile.* | Optimized builds for Agent, UI, and LiteLLM. |
| Orchestration | docker-compose.yaml | Defines the complete service stack with networking and volumes. |
| Startup Script | scripts/start_node.sh | One-click build and deploy automation. |

**Status:** ✅ **DONE**. The entire system is containerized and deployable via `start_node.sh`.

---

## **🔟 Phase 10 – Multi-Project DevStudio (PLANNED)**

> [!CAUTION]
> **Critical Architectural Pivot Required**
> 
> The current architecture violates the **Principle of Least Authority (PoLA)**. Agents currently have write access to their own source code, creating a **Confused Deputy Problem**.

| Deliverable | File | Function |
| :---- | :---- | :---- |
| Project Registry | `src/persistence/migrations/2025_11_21_project_registry.sql` | Stores metadata for external projects managed by DevStudio. |
| Isolation Layer | `docker-compose.yaml` | Mounts DevStudio `src/` as **read-only** and creates separate `/app/target_project/` execution volume. |
| FileTreeReader Tool | `src/tools/file_tree_reader.py` | Read-only tool for introspecting external projects. |
| Project API | `src/api/project_api.py` | New endpoints: `GET /api/projects/list`, `POST /api/sessions/start/{project_id}`. |

**Status:** 🚧 **PLANNED**. DevStudio must transition from managing its own codebase to being a **Multi-Project IDE Backend** that securely manages external codebases.

**Full Details:** See [Phase 10 Architectural Mandate](../feedback/phase_10_architectural_mandate.md)

---

## **Future Roadmap (Beyond Phase 10)**

- **Multi-Node Clustering**: Scaling beyond a single machine.
- **Advanced Governance**: Human-in-the-loop approval workflows for high-risk tools.
- **Marketplace**: Dynamic loading of third-party agent skills.


