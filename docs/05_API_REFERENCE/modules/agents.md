# Agents API Reference

This document provides an overview of all public agent classes in the **maf‑local** project.

## LiaisonAgent (Tier 1)
- **Location:** `src/agents/liaison_agent.py`
- **Purpose:** Classifies incoming user messages and routes them to the appropriate downstream agent.
- **Key Methods:**
  - `handle_user_message(message: str) -> str` – Asynchronously processes user input, classifies intent, and forwards to Project Lead if applicable.

## ProjectLeadAgent (Tier 2)
- **Location:** `src/agents/project_lead_agent.py`
- **Purpose:** Generates strategic plans (`StrategicPlan`) and coordinates workflow execution.
- **Key Methods:**
  - `receive_idea(idea: str) -> str` – Entry point for new project ideas.
  - `submit_strategic_plan(target_domains, tasks, plan_context) -> str` – (Tool) Generates and executes a strategic plan via OLB.

## DocumentationAgent (Tier 2)
- **Location:** `src/agents/documentation_agent.py`
- **Purpose:** Provides knowledge‑gate and PoLA enforcement for documentation‑related queries.
- **Key Methods:**
  - `process(query: str) -> str`

## Domain Leads (Tier 3)
- **BaseDomainLead** – Abstract base class (`src/agents/domain_leads/base_domain_lead.py`).
- **DevDomainLead** – Implements development‑task execution.
- **DocsDomainLead** – Implements documentation‑task execution.
- **QADomainLead** – *Planned but not yet implemented.*

Each domain lead breaks down a high‑level task into subtasks and dispatches them to the appropriate executor via the TLB workflow.
