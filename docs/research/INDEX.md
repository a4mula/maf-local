---
access: read-only
audience: agents | humans
update_trigger: new_research_added
managed_by: Humans (via DocUpdatePlanner for cataloging)
---

# Research: INDEX

> [!NOTE]
> This directory contains **reference material and background research**.  
> Agents should treat these as **READ-ONLY**. For active work, see [`planning/CURRENT.md`](../planning/CURRENT.md).

---

## Purpose

Research documents provide:
- Technical standards and specifications
- Background context for architectural decisions
- External references for compliance/integration

**Access Rule:** Agents can **read** but should **not modify** research docs. Updates require human approval or structured workflow.

---

## Research Documents

### **1. MAF SDK Standards** [`maf_sdk_standards.md`](./maf_sdk_standards.md)

**Type:** Technical Reference  
**Purpose:** Microsoft Agent Framework (MAF SDK) compliance requirements

**Key Sections:**
- Workflow orchestration (`WorkflowBuilder`, `Executor`, `Edge`)
- State management (`AgentThread`)
- Memory persistence (`Context Providers`)
- Checkpointing (`CheckpointStorage`)
- Coding standards (async I/O, type hints)

**When to Consult:**
- Before creating new agents
- During architecture decisions
- When implementing memory/checkpoint features
- For compliance audits

**Status:** ✅ Authoritative - Referenced in [GUIDELINES.md](../.ai/GUIDELINES.md)

---

### **2. Documentation Systems Research** [`documentation_systems_research.md`](./documentation_systems_research.md)

**Type:** Background Research  
**Purpose:** Understanding Diataxis framework and documentation best practices

**Key Sections:**
- Diataxis quadrants (Tutorials, How-To, Reference, Explanation)
- Agent-first documentation patterns
- CURRENT + ARCHIVE temporal patterns
- Documentation update workflows

**When to Consult:**
- Before adding new documentation
- When designing documentation structure
- For understanding "why" behind docs/ organization

**Status:** ✅ Applied - Implemented in current docs/ structure

---

## Adding New Research

To add a new research document:

1. **Create file:** `docs/research/[topic].md`
2. **Add frontmatter:**
   ```yaml
   ---
   access: read-only
   audience: agents | humans | both
   last_updated: YYYY-MM-DD
   tags: [tag1, tag2]
   ---
   ```
3. **Update this INDEX:**
   - Add entry with title, type, purpose, key sections
   - Specify "when to consult" guidelines
4. **Reference in relevant docs:**
   - Link from `GUIDELINES.md` if it affects coding standards
   - Link from `architecture/DECISIONS.md` if it justifies a design choice

---

## Research vs. Other Docs

| Need | Use This |
|:---|:---|
| **External standards/specs** | `research/` (read-only reference) |
| **Our architecture** | `architecture/CURRENT.md` |
| **Why we made a decision** | `why/RATIONALE.md` or `architecture/DECISIONS.md` |
| **How-to guide** | `guides/` |
| **Current phase work** | `planning/CURRENT.md` |

---

## Template: Research Document

```markdown
---
access: read-only
audience: agents | humans | both
last_updated: YYYY-MM-DD
tags: [tag1, tag2]
source: [URL or citation if external]
---

# [Topic] Research

## Overview
[Brief description of what this research covers]

## Key Points
- [Important finding 1]
- [Important finding 2]

## Sections
### Section 1
[Content]

### Section 2
[Content]

## References
- [External link 1]
- [External link 2]
```

**Note:** Keep research docs authoritative and stable. Frequent updates suggest it should be in `planning/` or `architecture/` instead.
