---
type: reference
audience: all
status: published
last_updated: 2025-11-21
related:
  - ../.ai/project_guidelines.md
  - ../architecture/CURRENT_STATE.md
tags: [maf-sdk, standards, compliance, microsoft]
feature_refs: []
---

# Microsoft Agent Framework (MAF SDK) Standards

**Source:** Official Microsoft Learn documentation  
**Purpose:** Reference for MAF SDK compliance and best practices

---

## I. MAF Foundation and LLM Optimization Standards

### 1.1 Framework Mandate and Architectural Overview

The **Microsoft Agent Framework (MAF)** constitutes an open-source development kit intended for the construction of sophisticated AI agents and multi-agent workflows across both the .NET and Python ecosystems. The framework is architecturally significant as the unified foundation for future agent development from Microsoft, serving as the direct successor to and integration point for key concepts pioneered by **Semantic Kernel (SK)** and **AutoGen** projects.

#### 1.1.1 MAF as the Unified Agent Foundation

MAF successfully integrates the strengths of its predecessors. It inherits AutoGen's straightforward abstractions for single- and multi-agent patterns, while incorporating Semantic Kernel's enterprise-grade features. This unification delivers crucial capabilities such as thread-based state management, strong type safety across component messaging, advanced filtering, and comprehensive telemetry integration.

The framework distinctly divides its capabilities into two categories:
1. **AI Agents**: Core individual units utilizing Large Language Models (LLMs) to process user inputs, make decisions, invoke tools, and communicate with Model Context Protocol (MCP) servers
2. **Workflows**: Graph-based system for orchestrating complex, multi-step tasks by connecting multiple agents and deterministic functions

#### 1.1.2 The MAF Architectural Separation

The architectural robustness of MAF is rooted in its highly modular composition. Key foundational building blocks include:

- **Model Clients**: For chat completions and responses
- **Agent Thread**: Management for state
- **Context Providers**: For agent memory
- **Middleware**: For intercepting actions
- **MCP Clients**: For secure tool integration

> [!IMPORTANT]
> **Critical Design Decision**: The separation of state management and memory into dedicated, pluggable components—the **Agent Thread** and **Context Providers**—is crucial for enterprise reliability. This structural decoupling ensures that the system's operational stability remains consistent regardless of the underlying LLM provider or model version being utilized.

---

## II. Agent Core: API Surface and Component Relations (Python SDK)

### 2.1 Initializing the Python Agent Environment

#### 2.1.1 Package and Import Structure

MAF Python packages are distributed through the PyPI feed, where all official packages adhere to the prefix standard `microsoft-agents-a365`.

**Breaking Change Alert:**
```python
# ❌ Old (deprecated)
from microsoft.agents import ChatAgent

# ✅ New (correct)
from microsoft_agents.hosting.core import TurnContext
```

#### 2.1.2 Authentication and Client Setup

MAF mandates robust handling of credentials and identity. For Azure services, `AzureCliCredential` is the default mechanism (requires `az login`).

**Cloud-Agnostic Design:**
The architecture maintains a cloud-agnostic approach. While Azure identity integration is prioritized, the system explicitly permits replacing `AzureCliCredential` with `ApiKeyCredential`. This design choice confirms that MAF functions primarily as a **vendor-neutral orchestration layer**, allowing developers to deploy agents across various environments.

---

### 2.2 Foundational Agent Building Blocks (Python API Reference)

| Class Name | Module Path | Core Function | Dependency/Relationship |
| :--- | :--- | :--- | :--- |
| `AIFunction` | `agent_framework.core` | Tool/Function Wrapper & Schema Generator | Requires type-hinted Python function |
| `AgentExecutor` | `agent_framework.workflow` | Executes AIAgent within a graph workflow | Wraps an AIAgent |
| `AgentThread` | `agent_framework.core` | Multi-Turn State/Context Management | Required for conversational context |
| `Context Provider` | `agent_framework.memory` | Persistent Agent Memory Interface | Interacts with external storage |

#### 2.2.1 AIFunction (Tool/Function Wrapper)

The `AIFunction` class serves as the standardized tool wrapper, enabling deterministic Python functions to be callable by AI models. Its key utility lies in its capability to **automatically generate a JSON schema** representing the function's inputs and outputs based on Python type hints.

#### 2.2.2 AgentThread (State Management)

The `AgentThread` component is responsible for managing the state and maintaining conversational context across multi-turn interactions. It abstracts away the technical differences between various threading types supported by underlying services.

#### 2.2.3 Context Providers (Memory Interface)

Context Providers are the **pluggable interfaces** used to manage persistent agent memory. For enterprise systems, the Python SDK includes:
- `microsoft_agents.storage.blob` - Azure Blob storage
- `microsoft_agents.storage.cosmos` - CosmosDB integration

> [!CAUTION]
> **Violation Risk**: If code is directly accessing PostgreSQL or ChromaDB without implementing the MAF's official `Context Providers` interface, it constitutes **architectural drift**.

---

## III. Declarative Agent Definition: The Manifest Schema

### 3.1 Agent Manifest Structure (YAML/JSON Schema)

The Agent Manifest (typically `manifest.yaml`) is the required declarative configuration for defining the agent's identity, operational logic, instructions, and required tools.

**Key Fields:**

| Field Name | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `Descriptor:Name` | String | True | Unique identifier for agent referencing |
| `SkillGroups:Format` | String (Enum) | True | Type of skill (e.g., AGENT, GPT) |
| `Skills:Name` | String | True | Internal name referencing the implementation |
| `Interfaces:Agent Inputs` | Sequence (List) | True | Mandatory input arguments |
| `Settings:Model` | String | True | LLM identifier (e.g., gpt-4o-mini) |
| `Settings:Instructions` | Multiline String | True | System prompt guiding agent behavior |
| `ChildSkills` | Sequence (List) | Optional | Tools/skills callable by this skill |

### 3.2 Best Practice: Defining Tools and Instructions

#### Instruction Optimization

The `Settings:Instructions` field holds the system prompt, which must be clearly bounded and explicit. Best practices involve using specific delimiters:

```yaml
Settings:
  Instructions: |
    <|im_start|>system
    You are a Security Agent. Follow the chain of reasoning exactly:
    1. Extract the hostname using 'ExtractHostname_Tool'.
    2. Resolve DNS using 'GetDnsResolutions' on the extracted hostname.
    3. Use 'lookupIpAddressGeolocation' sequentially for each IP.
    Return a final, consolidated security report.
    <|im_end|>
```

#### Tool Scoping via ChildSkills

The manifest allows developers to list explicit `ChildSkills` nested under a parent skill. This provides a critical mechanism for **runtime tool scoping**, significantly increasing the determinism of the agent's execution path.

---

## IV. Advanced Workflow Orchestration and Execution

### 4.1 Workflow Architecture (agent_framework.workflow)

Workflows in MAF provide the system for multi-agent coordination and complex procedural execution. The execution engine operates based on a **graph structure**, utilizing a Pregel-like model for execution.

**Benefits:**
- **Modularity**: Complex tasks broken into reusable Executor components
- **Flexible Flow**: Conditional routing, parallel processing, dynamic paths
- **Type Safety**: Strong typing on messages between components
- **Checkpointing**: Saving workflow state for recovery and resumption

> [!WARNING]
> **Compliance Mandate**: Workflows must be built using the MAF SDK's graph-based system and its components (`Executor`, `Edge`, `WorkflowBuilder`). Any custom implementation must be refactored to use the SDK's native classes.

### 4.2 Executors (Nodes)

Executors are the fundamental, autonomous processing units within a workflow graph.

**Key Executor Types:**

| Executor Type | Base Class | I/O Message Type | Use Case Example |
| :--- | :--- | :--- | :--- |
| `AgentExecutor` | `ReflectingExecutor` | Message / AgentRunEvent | LLM-based reasoning or tool execution |
| `RequestInfoExecutor` | `ReflectingExecutor` | WorkflowRequestEvent | Human-in-the-loop (HITL) scenarios |
| `ConditionalRouter` | `ReflectingExecutor` | Variable (Boolean or Typed) | Branching based on conditions |
| `ReflectingExecutor` | object | Variable | Base class for custom, deterministic nodes |

### 4.3 Edges (Connections)

Edges define the control and data paths between Executors. The framework supports:
- **Direct Edges**: Linear message flow
- **Conditional Edges**: Evaluate output to determine routing
- **Fan-out Edges**: Concurrent message distribution
- **Fan-in Edges**: Aggregation of multiple upstream messages

---

## V. Enterprise Integration and Deployment Best Practices

### 5.1 Cloud Agnostic Deployment Model

The Microsoft Agent Framework is purposefully designed to be highly portable, positioning itself as a **platform-agnostic orchestrator**. Agents can be deployed across:
- Containers
- On-premises systems
- Multiple cloud platforms

This portability is achieved through vendor-neutral abstractions and commitment to open standards (MCP, Agent-to-Agent (A2A), OpenAPI).

### 5.2 Enterprise Capabilities and Governance (Agent 365 Context)

While MAF provides the open-source orchestrator runtime, achieving full enterprise readiness requires leveraging the proprietary **Microsoft 365 Agent SDK (Agent 365)**.

**Relationship:**
- **MAF**: Flexible, open execution layer (this project uses this)
- **Agent 365**: Mandatory Enterprise Capabilities layer (out of scope for local-first mandate)

**Agent 365 Features:**
- Unified identity management
- Governance and auditing
- Enterprise-grade telemetry
- Secure Microsoft 365 data integration via MCP connectors

### 5.3 Python Coding Standards and Maintainability

> [!IMPORTANT]
> **Mandatory Coding Standards for MAF SDK Compliance**

#### 1. Asynchronous Development

All logic must utilize Python's `asyncio` framework for non-blocking I/O:

```python
# ✅ Correct
async def process_message(message: str) -> str:
    response = await llm_client.chat(message)
    return response

# ❌ Wrong (blocking)
def process_message(message: str) -> str:
    response = llm_client.chat(message)  # This blocks!
    return response
```

#### 2. Type Safety (Mandatory)

Python type hints are **mandatory** across all function signatures. This is required for:
- `AIFunction` to generate accurate JSON schemas
- Strong type-safe message passing in workflow engine

```python
# ✅ Correct
async def calculate_risk(
    transaction_amount: float,
    user_history: Dict[str, Any]
) -> Dict[str, float]:
    ...

# ❌ Wrong (no types)
async def calculate_risk(transaction_amount, user_history):
    ...
```

---

## VI. Compliance Checklist for MAF Local

### Documentation Identity
- [x] All references to "Modular Agent Framework" replaced with "Microsoft Agent Framework (MAF SDK)"
- [ ] All conceptual docs audited

### Code Compliance

| Requirement | MAF SDK Standard | Current Status | Action Required |
| :--- | :--- | :--- | :--- |
| **State Management** | Use `AgentThread` for temporal state | ❓ AUDIT REQUIRED | Verify not directly accessing PostgreSQL for state |
| **Memory** | Use `Context Providers` interface | ❓ AUDIT REQUIRED | Verify not directly accessing ChromaDB without provider interface |
| **Workflows** | Use `WorkflowBuilder`, `Executor`, `Edge` | ❓ AUDIT REQUIRED | Audit `maf_workflow.py` for compliance |
| **Async I/O** | All I/O operations must use `asyncio` | ❓ AUDIT REQUIRED | Review all agent code |
| **Type Hints** | All function signatures must have types | ❓ AUDIT REQUIRED | Review all agent code |

---

## References

1. [Introduction to Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
2. [Microsoft Agent Framework Quick-Start Guide](https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start)
3. [agent_framework package | Microsoft Learn](https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework?view=agent-framework-python-latest)
4. [Microsoft Agent 365 SDK for Python](https://learn.microsoft.com/en-us/python/api/agent365-sdk-python/agent365-overview?view=agent365-sdk-python-latest)
5. [Introducing Microsoft Agent Framework Blog](https://devblogs.microsoft.com/foundry/introducing-microsoft-agent-framework-the-open-source-engine-for-agentic-ai-apps/)

---

**For full detailed reference**, see the complete txt file (525 lines) that was converted to this markdown.