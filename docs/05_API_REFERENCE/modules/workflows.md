# Workflows API Reference

This document describes the public workflow classes and functions.

## OLBWorkflow
- **Location:** `src/workflows/olb_workflow.py`
- **Purpose:** Routes a `StrategicPlan` from the `ProjectLeadAgent` to the appropriate domain leads.
- **Key Methods:**
  - `execute_plan(plan: StrategicPlan, thread: AgentThread) -> dict` – Executes the plan and returns an aggregated result.

## ResearchWorkflow
- **Location:** `src/workflows/research_workflow.py`
- **Purpose:** Performs a two‑step research process (research → summarize) using a `CoreAgent`.
- **Key Functions:**
  - `build_research_workflow(agent: CoreAgent) -> WorkflowGraph`

## MainOrchestrator
- **Location:** `src/workflows/main_orchestrator.py`
- **Purpose:** Core workflow engine that runs a directed graph of workflow nodes.
- **Key Methods:**
  - `run(initial_context: Optional[WorkflowContext] = None) -> WorkflowContext`
