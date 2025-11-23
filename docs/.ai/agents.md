# Agent Personas

**Purpose:** Define agent personas, responsibilities, and boundaries for the MAF Local project.

**Last Updated:** 2025-11-23

---

## Current Architecture (Simplified MVP)

MAF Local currently implements a **2-tier architecture** following the "MVP-first" approach. The multi-tier hierarchy (DomainLeads, Executors) was temporarily removed during the Emergency Refactor and will be reintroduced incrementally.

---

## @liaison (Liaison Agent)

**Tech Stack:** Python, MAF ChatAgent, FastAPI  
**Model:** LiteLLM Proxy (Ollama + Gemini fallback)  
**Implementation:** [`src/agents/liaison_agent.py`](file:///home/robb/projects/maf-local/src/agents/liaison_agent.py)

### Responsibilities
- **User Interface**: Handle all direct user interactions via Streamlit/API
- **Intent Classification**: Determine if user input is a Question or an Idea
- **Clarification**: Ask follow-up questions to eliminate ambiguity
- **Delegation**: Forward classified intents to Project Lead

### Boundaries
- ❌ **Cannot**: Make technical decisions
- ❌ **Cannot**: Execute tools or modify code
- ❌ **Cannot**: Access databases directly
- ✅ **Can**: Read user messages
- ✅ **Can**: Ask clarifying questions
- ✅ **Can**: Forward to Project Lead

### Tools Available
- None (purely conversational)

---

## @project-lead (Project Lead Agent)

**Tech Stack:** Python, MAF ChatAgent, Universal Tools  
**Model:** LiteLLM Proxy (Ollama + Gemini fallback)  
**Implementation:** [`src/agents/project_lead_agent.py`](file:///home/robb/projects/maf-local/src/agents/project_lead_agent.py)

### Responsibilities
- **Decision Making**: Make technical decisions for user requests
- **Tool Execution**: Execute tools via MAF's `@use_function_invocation` decorator
- **File Generation**: Create files on disk using `write_file` tool
- **Code Execution**: Run Python code using `execute_code` tool (sandboxed)

### Boundaries
- ❌ **Cannot**: Delegate to Domain Leads (not yet implemented)
- ❌ **Cannot**: Create workflows (future feature)
- ✅ **Can**: Execute tools directly
- ✅ **Can**: Create files on disk
- ✅ **Can**: Run code evaluations
- ✅ **Can**: Read project context

### Tools Available
- `write_file` - Create files with path validation
- `execute_code` - Execute Python code (sandboxed via io.StringIO)

**Current Pattern:** Tools registered as `AIFunction` objects using `@ai_function` decorator. Execution handled automatically by MAF framework.

---

## Archived Agents (Temporarily Removed)

The following agents were removed during the Emergency Refactor (November 2025) and will be reintroduced incrementally with proper MAF Workflow orchestration:

### @dev-lead, @qa-lead, @docs-lead (Domain Lead Agents)
**Status:** Deleted  
**Reason:** Premature complexity - proving 2-tier MVP first  
**Future:** Will reintegrate with MAF Workflow graphs

### @coder, @tester, @writer (Executor Agents)
**Status:** Deleted  
**Reason:** Execution layer needed to be proven first  
**Future:** Will add as workflow nodes under Domain Leads

### @governance (Governance Agent)
**Status:** Deleted  
**Reason:** Decision logging can be added after MVP  
**Future:** Will reintroduce for audit trail

### @context-retrieval (Context Retrieval Agent)
**Status:** Deleted  
**Reason:** Context injection simplified to file reading  
**Future:** Will add semantic RAG capabilities

### @artifact-manager (Artifact Manager Agent)
**Status:** Deleted  
**Reason:** File operations handled by tools now  
**Future:** Will add for advanced file management

---

## Tool Execution Pattern

**Current Implementation (MAF-Compliant):**

```python
# LiteLLMChatClient extends BaseChatClient
@use_function_invocation
class LiteLLMChatClient(BaseChatClient):
    async def _inner_get_response(...):
        # Convert MAF -> OpenAI -> MAF
        # Framework handles tool execution loop automatically
```

**How it works:**
1. Tools defined as `UniversalTool` in `universal_tools.py`
2. Exported as `AIFunction` via `registry.get_ai_functions()`
3. Passed to `ChatAgent` during initialization
4. `@use_function_invocation` decorator intercepts responses
5. Framework executes tools and feeds results back to LLM
6. No custom execution loop required

---

## Future Roadmap

### Phase 5: Domain Lead Reintegration
- Re-add DomainLeadAgent classes (Dev, QA, Docs)
- Implement MAF Workflow orchestration
- Add delegation from ProjectLead → DomainLeads

### Phase 6: Executor Layer
- Add ExecutorAgent classes (Coder, Tester, Writer)
- Assign to Domain Leads via workflow nodes
- Implement task atomicity and escalation

### Phase 7: Governance & Context
- Reintroduce GovernanceAgent for decision logging
- Add ContextRetrievalAgent for semantic RAG
- Integrate with PostgreSQL + ChromaDB

---

## Agent Communication

**Current Pattern:**
```
User → Streamlit → API → Liaison → ProjectLead → Tools → Response
```

**Future Pattern (Multi-Tier):**
```
User → Liaison → ProjectLead → DomainLead → Executor → Tools → Response
                      ↓
                 Governance (audit log)
                      ↓
                 ContextRetrieval (RAG)
```

---

## Best Practices

When working with agents:
1. **Respect boundaries** - Each agent has limited capabilities
2. **Use MAF patterns** - Leverage `ChatAgent`, `AIFunction`, decorators
3. **Test incrementally** - Prove each layer works before adding more
4. **Follow MVP-first** - Simplicity over architecture
