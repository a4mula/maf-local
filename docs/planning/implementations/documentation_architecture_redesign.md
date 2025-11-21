# Documentation Architecture Redesign

**Status:** 🚧 PLANNING  
**Created:** 2025-11-21  
**Priority:** HIGH

---

## Problem Statement

Current documentation structure violates **DRY principle** and lacks consistent patterns:

### Issues Identified

1. **Inconsistent Patterns**
   - ❌ Planning has CURRENT + ARCHIVE
   - ❌ Feedback has individual files (no CURRENT/ARCHIVE)
   - ❌ Architecture has no archive pattern
   - ❌ Explanation has individual files

2. **Redundancy**
   - `tutorials/` vs `how-to/` - Same purpose, different names
   - `vision/ideal_state.md` vs `planning/roadmap.md` - Overlapping content
   - Multiple "ideal state" documents in vision/

3. **`.ai/` Folder Chaos**
   - 7 files with inconsistent naming
   - No clear ownership or update guidelines
   - Duplicate information (AGENT_INSTRUCTIONS vs project_guidelines)

4. **Unclear Relationships**
   - How does Vision relate to Planning?
   - How does Feedback feed into Planning?
   - What's the difference between Roadmap and Phase_Planner_ARCHIVE?

5. **Research Organization**
   - Who can write? When? For what purpose?
   - How do agents use research vs reference it?

---

## Proposed Solution: Universal CURRENT + ARCHIVE Pattern

Apply consistent pattern across **ALL** documentation categories:

```
docs/
├── .ai/                          ← Agent workspace (standardized)
│   ├── MANIFEST.yaml            ← Single source of features/config
│   ├── AGENTS.md                ← Agent roles & tools
│   └── GUIDELINES.md            ← Coding standards
│
├── planning/
│   ├── CURRENT.md               ← Active phase
│   ├── ARCHIVE.md               ← Summarized history
│   └── implementations/         ← Detailed plans (cleaned up post-phase)
│
├── feedback/
│   ├── CURRENT.md               ← Active feedback/audits
│   └── ARCHIVE.md               ← Resolved feedback summaries
│
├── architecture/
│   ├── CURRENT.md               ← Current system state
│   └── DECISIONS.md             ← ADRs (Architecture Decision Records)
│
├── why/                         ← Renamed from "explanation"
│   └── RATIONALE.md             ← Single doc with all "why" justifications
│
├── guides/                      ← Merged tutorials + how-to
│   ├── QUICKSTART.md            ← For humans
│   └── AGENT_ONBOARDING.md      ← For AI agents
│
├── research/
│   ├── INDEX.md                 ← Research catalog
│   └── [topic].md               ← Read-only research docs
│
└── vision/
    └── FUTURE.md                ← Long-term vision (single doc)
```

---

## Design Principles

### 1. Two-File Pattern (CURRENT + ARCHIVE)

**Every temporal category gets:**
- `CURRENT.md` - What's happening now
- `ARCHIVE.md` - Compressed history

**Benefits:**
- Agents know where to look
- Prevents file proliferation
- Clear temporal boundaries

### 2. Single-File Pattern (Global Context)

**Every reference category gets:**
- One authoritative file
- Indexed sections for navigation

**Examples:**
- `why/RATIONALE.md` - All "why" explanations
- `vision/FUTURE.md` - All future aspirations
- `.ai/GUIDELINES.md` - All coding standards

### 3. Agent-First Organization

**Every document answers:**
- **WHO** can read/write this?
- **WHEN** should it be consulted?
- **HOW** should it be updated?

Add YAML frontmatter:
```yaml
---
access: read-only | read-write
audience: agents | humans | both
update_trigger: phase_complete | feedback_received | architecture_change
---
```

---

## Detailed Redesign

### `.ai/` Folder Cleanup

**BEFORE** (7 files, chaos):
```
.ai/
├── AGENT_INSTRUCTIONS.md      ← Duplicate of guidelines
├── CHECKLIST.md               ← Unclear purpose
├── SYSTEM_OVERVIEW.md         ← Duplicate of CURRENT_STATE
├── agents.md                  ← Agent roles
├── feature_manifest.yaml      ← Features
├── project_guidelines.md      ← Standards
└── update_templates.yaml      ← Doc templates
```

**AFTER** (3 files, clear):
```
.ai/
├── MANIFEST.yaml              ← Features + config (merged feature_manifest + update_templates)
├── AGENTS.md                  ← Agent roles, tools, hierarchy
└── GUIDELINES.md              ← Coding standards (merged project_guidelines + AGENT_INSTRUCTIONS)
```

**Rationale:**
- 1 file per concern
- Agents read MANIFEST for features
- GUIDELINES for standards (async, type hints, MAF SDK)
- AGENTS for hierarchy

---

### Planning Consolidation

**BEFORE** (5 files):
```
planning/
├── CURRENT_PHASE.md           ← Active phase
├── Phase_Planner_ARCHIVE.md   ← History
├── roadmap.md                 ← ???
├── maf_sdk_compliance_implementation.md  ← Detailed plan
└── phase_management_workflow.md          ← Meta process
```

**AFTER** (3 files + folder):
```
planning/
├── CURRENT.md                 ← Active phase (renamed from CURRENT_PHASE)
├── ARCHIVE.md                 ← History (renamed from Phase_Planner_ARCHIVE)
├── WORKFLOW.md                ← Meta process (how to use planning docs)
└── implementations/           ← Detailed plans (archived post-phase)
    └── maf_sdk_compliance_implementation.md
```

**Changes:**
- **Delete `roadmap.md`** - Content merged into ARCHIVE.md header
- **Rename files** for consistency
- **implementations/** folder for detailed plans (cleaned up after phase complete)

---

### Feedback Consolidation

**BEFORE** (3 separate files):
```
feedback/
├── maf-local_feedback_v2.md
├── maf_sdk_compliance_audit.md
├── phase_10_architectural_mandate.md
```

**AFTER** (2 files):
```
feedback/
├── CURRENT.md                 ← Active feedback for current phase
└── ARCHIVE.md                 ← Resolved feedback summaries
```

**Migration:**
- Current phase feedback → `CURRENT.md`
- Resolved feedback → Summarize in `ARCHIVE.md`, delete original

**Format:**
```markdown
# Feedback: CURRENT

## Phase 10.1: MAF SDK Compliance
[Details of current audit/feedback]

---
# When feedback resolved, move to ARCHIVE.md as:
## [Phase X] - [Topic] (Resolved YYYY-MM-DD)
Brief summary. Link to detailed docs if preserved.
```

---

### Architecture Simplification

**BEFORE** (1 file):
```
architecture/
└── CURRENT_STATE.md
```

**AFTER** (2 files):
```
architecture/
├── CURRENT.md                 ← System state (diagram, components)
└── DECISIONS.md               ← ADR log (Architecture Decision Records)
```

**Rationale:**
- CURRENT.md - "What is the system?"
- DECISIONS.md - "Why did we build it this way?"

---

### Explanation → Why (Rename + Consolidate)

**BEFORE**:
```
explanation/
└── why_hierarchical_agents.md
```

**AFTER**:
```
why/
└── RATIONALE.md
```

**Format:**
```markdown
# Architectural Rationale

## Why Hierarchical Agents?
[Content from why_hierarchical_agents.md]

## Why MAF SDK?
[Explanation of framework choice]

## Why ChromaDB?
[Memory persistence rationale]
```

**Benefit:** Single source for all "why" questions

---

### Tutorials + How-To → Guides (Merge)

**BEFORE** (redundant):
```
tutorials/
└── 01_quickstart.md

how-to/
└── deploy_with_docker.md
```

**AFTER** (unified):
```
guides/
├── QUICKSTART.md              ← For humans (getting started)
├── AGENT_ONBOARDING.md        ← For AI agents (what to read first)
└── DEPLOYMENT.md              ← Ops guide (Docker, production)
```

**Diataxis Justification:**
- **Tutorials** = Learning-oriented (QUICKSTART covers this)
- **How-To** = Task-oriented (DEPLOYMENT covers this)
- No need for separate directories

---

### Vision Consolidation

**BEFORE** (multiple files):
```
vision/
├── ideal_state.md
└── 🎯 Ideal State_ The Hierarchical MAF Studio.md
```

**AFTER** (single file):
```
vision/
└── FUTURE.md
```

**Content:** Merge both files, organize by:
1. Short-term goals (next 3-6 months)
2. Medium-term vision (6-12 months)
3. Long-term aspirations (1+ years)

---

### Research Organization

**BEFORE** (unclear):
```
research/
├── documentation_systems_research.md
└── maf_sdk_standards.md
```

**AFTER** (cataloged):
```
research/
├── INDEX.md                   ← Catalog of research docs
├── documentation_systems.md   ← Renamed for consistency
└── maf_sdk_standards.md       ← Reference
```

**Access Rules (in INDEX.md):**
- **Agents: READ-ONLY** (reference material)
- **Humans: WRITE** (via `DocUpdatePlanner` or manual editing)
- **Purpose:** Background research, standards reference

---

## File Type Taxonomy

| Type | Pattern | Example | Agent Access |
|:---|:---|:---|:---|
| **Temporal** | CURRENT + ARCHIVE | planning/, feedback/ | Read/Write CURRENT, Read ARCHIVE |
| **Reference** | Single global file | why/RATIONALE.md | Read-only (append via structured process) |
| **Config** | YAML/MD | .ai/MANIFEST.yaml | Read-only (update via tools) |
| **Guides** | Multiple guides | guides/QUICKSTART.md | Read-only (versioned updates) |

---

## Migration Plan

### Phase 1: Audit & Cleanup (2 hours)
1. Create new directory structure
2. Create empty CURRENT/ARCHIVE stubs
3. Catalog existing content

### Phase 2: Content Migration (3 hours)
1. Merge `.ai/` files → 3 files
2. Consolidate feedback → CURRENT + ARCHIVE
3. Merge vision files → FUTURE.md
4. Merge tutorials + how-to → guides/
5. Rename explanation → why/

### Phase 3: Update References (1 hour)
1. Update INDEX.md with new structure
2. Update README.md links
3. Update AGENT_INSTRUCTIONS references
4. Update task.md patterns

### Phase 4: Validation (1 hour)
1. Verify all links work
2. Check YAML frontmatter
3. Test agent navigation
4. Document new structure in WORKFLOW.md

---

## Success Criteria

- [ ] All categories follow CURRENT + ARCHIVE OR single-file pattern
- [ ] `.ai/` folder has exactly 3 files
- [ ] No redundant directories (tutorials vs how-to)
- [ ] Clear relationship: Vision → Planning → Implementation → Feedback → Archive
- [ ] Every doc has YAML frontmatter with access rules
- [ ] Updated `docs/INDEX.md` reflects new structure
- [ ] Phase management workflow updated

---

## Post-Migration Standards

### When to Update Each Doc

| Document | Update Trigger | Who Updates |
|:---|:---|:---|
| `planning/CURRENT.md` | New phase starts | Agent (via tool) |
| `planning/ARCHIVE.md` | Phase completes | Agent (compression) |
| `feedback/CURRENT.md` | Audit/feedback received | Agent or Human |
| `feedback/ARCHIVE.md` | Feedback resolved | Agent (summarize) |
| `architecture/CURRENT.md` | Architecture changes | Agent (after code change) |
| `architecture/DECISIONS.md` | Design decision made | Human or Agent (ADR template) |
| `why/RATIONALE.md` | New "why" question | Append via structured process |
| `.ai/MANIFEST.yaml` | Feature added/removed | Agent (via feature tracking) |
| `.ai/GUIDELINES.md` | Standards change | Human approval required |

---

## Quick Reference

**Need to know what's happening now?** → `planning/CURRENT.md`

**Need to know what happened before?** → `planning/ARCHIVE.md` or `feedback/ARCHIVE.md`

**Need to know why something exists?** → `why/RATIONALE.md`

**Need to know how to do something?** → `guides/`

**Need to understand current system?** → `architecture/CURRENT.md`

**Need to know a design decision?** → `architecture/DECISIONS.md`

**Need to reference research?** → `research/INDEX.md`

**Need to see the future?** → `vision/FUTURE.md`

---

## Next Steps

1. **Get user approval** for this redesign
2. **Create implementation plan** with file-by-file migration
3. **Execute migration** systematically
4. **Update all references** in code and docs
5. **Document new patterns** in `.ai/GUIDELINES.md`
