# Agents API Reference

This document provides an overview of all public agent classes in the **maf‑local** project.

## LiaisonAgent (Tier 1)
- **Location:** `src/agents/liaison_agent.py`
- **Purpose:** Classifies incoming user messages and routes them to the appropriate downstream agent.
- **Key Methods:**
  - `process(message: str) -> str` – Returns the name of the target agent.
  - `handle(message: str) -> str` – Executes the routing logic.

## ProjectLeadAgent (Tier 2)
- **Location:** `src/agents/project_lead_agent.py`
- **Purpose:** Generates strategic plans (`StrategicPlan`) and coordinates workflow execution.
- **Key Methods:**
  - `plan(project_goal: str) -> StrategicPlan`
  - `execute_plan(plan: StrategicPlan) -> dict`

## DocumentationAgent (Tier 2)
- **Location:** `src/agents/documentation_agent.py`
- **Purpose:** Provides knowledge‑gate and PoLA enforcement for documentation‑related queries.
- **Key Methods:**
  - `process(query: str) -> str`

## Domain Leads (Tier 3)
- **BaseDomainLead** – Abstract base class (`src/agents/domain_leads/base_domain_lead.py`).
- **DevDomainLead** – Implements development‑task execution.
- **QADomainLead** – Implements QA‑task execution.
- **DocsDomainLead** – Implements documentation‑task execution.

Each domain lead breaks down a high‑level task into subtasks and dispatches them to the appropriate executor via the TLB workflow.
