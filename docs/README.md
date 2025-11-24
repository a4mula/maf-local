# MAF Local / DevStudio Documentation

**Welcome to the documentation for MAF Local (alias: DevStudio).**

This project is a **Microsoft Agent Framework (MAF)** implementation of a multi-agent system, orchestrated by the **Google Antigravity** meta-layer.

---

## 📚 Documentation Structure

The documentation is organized into 5 distinct layers to separate the "Meta" (Orchestration) from the "Project" (Implementation):

### [00_META](./00_META/) - Antigravity Orchestration Layer
*Documentation for the AI Agents (UPP, SRC, DOCS) building this project.*
*   **[ANTIGRAVITY_GUIDE.md](./00_META/ANTIGRAVITY_GUIDE.md)** - Guide to the orchestration system
*   **[WORKFLOW.md](./00_META/WORKFLOW.md)** - How the meta-agents collaborate
*   **[PHILOSOPHY.md](./00_META/PHILOSOPHY.md)** - Why we are building this way

### [01_ARCHITECTURE](./01_ARCHITECTURE/) - DevStudio System Design
*Technical specifications for the target project.*
*   **[CURRENT.md](./01_ARCHITECTURE/CURRENT.md)** - **The Source of Truth** for current system state
*   **[IDEAL.md](./01_ARCHITECTURE/IDEAL.md)** - The target 4-Tier architecture
*   **[DECISIONS.md](./01_ARCHITECTURE/DECISIONS.md)** - Architecture Decision Records (ADRs)
*   **[CONCEPTS.md](./01_ARCHITECTURE/CONCEPTS.md)** - Deep dive into MAF concepts

### [02_PLANNING](./02_PLANNING/) - Roadmap & Tasks
*Project management and history.*
*   **[TASKS.md](./02_PLANNING/TASKS.md)** - Active task list
*   **[ROADMAP.md](./02_PLANNING/ROADMAP.md)** - High-level phases
*   **[HISTORY/](./02_PLANNING/HISTORY/)** - Archived plans and completion reports

### [03_GUIDES](./03_GUIDES/) - User & Developer Guides
*How-to guides for using DevStudio.*
*   *(Coming Soon)* - Setup, Usage, Contribution guides

### [04_AGENTS](./04_AGENTS/) - DevStudio Agent Definitions
*Definitions for the agents WITHIN the DevStudio system.*
*   *(Coming Soon)* - Liaison, Project Lead, Domain Lead specs

---

## 🧭 Quick Navigation

| Need | Go To |
|:---|:---|
| **What is the system state?** | [`01_ARCHITECTURE/CURRENT.md`](./01_ARCHITECTURE/CURRENT.md) |
| **How do the Meta-Agents work?** | [`00_META/ANTIGRAVITY_GUIDE.md`](./00_META/ANTIGRAVITY_GUIDE.md) |
| **What are we working on?** | [`02_PLANNING/TASKS.md`](./02_PLANNING/TASKS.md) |
| **Why did we decide X?** | [`01_ARCHITECTURE/DECISIONS.md`](./01_ARCHITECTURE/DECISIONS.md) |

---

## 🤖 For Agents (Meta-Context)

**You are operating in the Antigravity Layer.**
*   **UPP:** Read `02_PLANNING` to plan.
*   **SRC:** Read `01_ARCHITECTURE` to implement.
*   **DOCS:** Maintain this structure. Ensure `01_ARCHITECTURE/CURRENT.md` matches reality.

**Key Distinction:**
*   `00_META` = Rules for YOU (The AI Team).
*   `01_ARCHITECTURE` = Rules for the CODE you are writing.
