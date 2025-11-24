# Current Architecture

**Last Updated:** November 24, 2025

## Overview

The Unified Batching Engine (UBE) is a 4-tier hierarchical multi-agent system designed for strict separation of concerns, deterministic routing, and scalable execution. It leverages the Microsoft Agent Framework (MAF) for all core primitives.

> [!IMPORTANT]
> **Architecture Status:** Phase 2 (UBE Expansion) is in progress. The system is transitioning from a 2-tier MVP to the full 4-tier target state.

## System Components

### 1. Agent Hierarchy (4-Tier UBE)

The architecture is strictly hierarchical, with communication mediated by Batching Workflows (OLB/TLB).

```
Tier 1: Interface
   [LiaisonAgent]
        ↓
Tier 2: Orchestration (Strategy)
   [ProjectLeadAgent] ↔ [DocumentationAgent] (Peers)
        ↓ (OLB Workflow)
Tier 3: Tactical (Domain Leads)
   [DevDomainLead] [QADomainLead] [DocsDomainLead]
        ↓ (TLB Workflow)
Tier 4: Execution (Atomic)
   [CoderExecutor] [TesterExecutor] [WriterExecutor]
```

### 2. Implementation Status

| Component | Tier | Status | Description |
| :--- | :--- | :--- | :--- |
| **LiaisonAgent** | 1 | ✅ Active | Intent classification, routing |
| **ProjectLeadAgent** | 2 | ✅ Active | Strategic planning, MAF-compliant |
| **DocumentationAgent** | 2 | ✅ Active | Knowledge gate, PoLA gatekeeper |
| **OLB Workflow** | - | 🚧 Planned | Routes plans to Domain Leads |
| **Domain Leads** | 3 | 🚧 Planned | Task breakdown, TLB orchestration |
| **TLB Workflow** | - | ✅ Active | Parallel executor orchestration |
| **Executors** | 4 | ✅ Active | Atomic task execution, report generation |

### 3. Key Mechanisms

#### Batching Workflows
- **OLB (Orchestration Level Batcher):** Routes `StrategicPlan` objects from Project Lead to Domain Leads using MAF `SwitchCaseEdgeGroup`.
- **TLB (Tactical Level Batcher):** Fans out tasks to Executors and aggregates `ExecutorReport` objects using MAF `FanIn` pattern.

#### Data Contracts (Pydantic)
- `TaskDefinition`: Atomic task specification.
- `StrategicPlan`: Output of Project Lead.
- `ExecutorReport`: Output of Executors.

#### Security & Governance
- **PermissionFilter:** MAF `FunctionMiddleware` enforcing Principle of Least Authority (PoLA).
- **Authorized File Writers:** Only `ProjectLeadAgent` and `DocumentationAgent` can write to disk.
- **Sandboxed Tools:** `write_file` and `execute_code` have strict path validation.

### 4. Tool System

**Status:** ✅ Pure MAF Compliance (Refactored Nov 24, 2025)

- **Registry:** Removed custom `UniversalTool` registry.
- **Implementation:** Tools defined as `@ai_function` with Pydantic input models.
- **Integration:** Agents import `ALL_TOOLS` directly.
- **Execution:** Handled natively by MAF `LiteLLMChatClient`.

## File Structure

```
maf-local/
├── src/
│   ├── agents/
│   │   ├── executors/        # Tier 4: Coder, Tester, Writer
│   │   ├── domain_leads/     # Tier 3: Dev, QA, Docs (Coming Soon)
│   │   ├── project_lead_agent.py
│   │   ├── documentation_agent.py
│   │   └── liaison_agent.py
│   ├── workflows/            # OLB and TLB implementations
│   ├── tools/                # MAF @ai_function tools
│   ├── models/               # Pydantic data contracts
│   ├── governance/           # PermissionFilter
│   └── ...
├── docs/                     # Documentation
└── tests/                    # Unit and Integration tests
```

## Recent Improvements (Nov 2025)

1.  **Executor Tier (Tier 4):** Implemented specialized agents for atomic tasks.
2.  **TLB Workflow:** Implemented orchestration for parallel execution.
3.  **Tool Refactor:** Eliminated technical debt, achieved 100% MAF compliance.
4.  **Governance:** Implemented `PermissionFilter` middleware.

## Next Steps

See `docs/planning/CURRENT.md` for the detailed Phase 2 roadmap.
