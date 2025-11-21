# MAF Local Documentation

**Welcome to the MAF Local documentation!**

This documentation follows the **CURRENT + ARCHIVE** pattern for temporal organization and the **Diataxis framework** for content types.

---

## Quick Navigation

| Need | Go To |
|:---|:---|
| **What's happening now?** | [`planning/CURRENT.md`](./planning/CURRENT.md) |
| **What happened before?** | [`planning/ARCHIVE.md`](./planning/ARCHIVE.md) |
| **Why does X exist?** | [`why/RATIONALE.md`](./why/RATIONALE.md) |
| **How do I do X?** | [`guides/`](./guides/) |
| **What is the system?** | [`architecture/CURRENT.md`](./architecture/CURRENT.md) |
| **Why was X decided?** | [`architecture/DECISIONS.md`](./architecture/DECISIONS.md) |
| **What needs fixing?** | [`feedback/CURRENT.md`](./feedback/CURRENT.md) |
| **What was fixed?** | [`feedback/ARCHIVE.md`](./feedback/ARCHIVE.md) |
| **What's the vision?** | [`vision/FUTURE.md`](./vision/FUTURE.md) |
| **Reference material?** | [`research/INDEX.md`](./research/INDEX.md) |
| **Agent config?** | [`.ai/`](./.ai/) |

---

## Documentation Structure

```
docs/
├── .ai/                      # Agent Workspace
│   ├── MANIFEST.yaml        # Features + templates
│   ├── AGENTS.md            # Agent roles & tools
│   └── GUIDELINES.md        # Coding standards
│
├── planning/                # Project Planning
│   ├── CURRENT.md           # Active phase
│   ├── ARCHIVE.md           # Completed phases
│   └── implementations/     # Detailed implementation plans
│
├── feedback/                # Audits & Feedback
│   ├── CURRENT.md           # Active feedback
│   └── ARCHIVE.md           # Resolved feedback
│
├── architecture/            # System Architecture
│   ├── CURRENT.md           # System state
│   └── DECISIONS.md         # Architecture Decision Records (ADRs)
│
├── guides/                  # How-To Guides
│   ├── QUICKSTART.md        # Getting started
│   └── DEPLOYMENT.md        # Deployment guide
│
├── why/                     # Conceptual Understanding
│   └── RATIONALE.md         # Architectural rationale
│
├── research/                # Reference Material
│   └── INDEX.md             # Research catalog
│
└── vision/                  # Future Plans
    └── FUTURE.md            # Long-term vision
```

---

## For Agents: Understanding This Documentation

### Access Patterns

Each document has YAML frontmatter specifying:
- **access:** `read-only` | `read-write`
- **audience:** `agents` | `humans` | `both`
- **update_trigger:** When to update this document
- **managed_by:** Who can update (agent vs human)

**Example:**
```yaml
---
access: read-write
audience: agents
update_trigger: phase_complete
managed_by: Agents during execution
---
```

### Temporal vs. Reference Docs

| Type | Pattern | Example | Agent Behavior |
|:---|:---|:---|:---|
| **Temporal** | CURRENT + ARCHIVE | `planning/`, `feedback/` | Read CURRENT for active work, write to CURRENT, summarize to ARCHIVE when done |
| **Reference** | Single file | `why/RATIONALE.md`, `vision/FUTURE.md` | Read for context, append new sections as needed |
| **Config** | YAML/MD | `.ai/MANIFEST.yaml` | Read for features, update via DocUpdatePlanner |

### Update Workflows

**When a phase completes:**
1. Update `planning/CURRENT.md` status
2. Summarize in `planning/ARCHIVE.md`
3. Update `architecture/CURRENT.md` with new components
4. Move resolved feedback from `feedback/CURRENT.md` to `feedback/ARCHIVE.md`

**When audit feedback received:**
1. Add to `feedback/CURRENT.md`
2. Reference in `planning/CURRENT.md` tasks
3. When resolved → summarize in `feedback/ARCHIVE.md`

**When design decision made:**
1. Add ADR to `architecture/DECISIONS.md`
2. Update `architecture/CURRENT.md` if system changed
3. Add rationale to `why/RATIONALE.md` if needed

---

## For Humans: Getting Started

### I'm new, where do I start?

1. **README.md** (project root) - Overview and setup
2. **[`guides/QUICKSTART.md`](./guides/QUICKSTART.md)** - Step-by-step getting started
3. **[`architecture/CURRENT.md`](./architecture/CURRENT.md)** - Understand the system
4. **[`planning/CURRENT.md`](./planning/CURRENT.md)** - See what's being worked on

### I want to understand the "why"

- **[`why/RATIONALE.md`](./why/RATIONALE.md)** - Why hierarchical agents? Why MAF SDK? Why FOSS-first?
- **[`architecture/DECISIONS.md`](./architecture/DECISIONS.md)** - Historical design decisions (ADRs)
- **[`vision/FUTURE.md`](./vision/FUTURE.md)** - Long-term vision and roadmap

### I need to do something

- **[`guides/`](./guides/)** - Task-oriented how-to guides
- **[`.ai/GUIDELINES.md`](./.ai/GUIDELINES.md)** - Coding standards and common patterns

### I found a bug or have feedback

- Add to **[`feedback/CURRENT.md`](./feedback/CURRENT.md)** (or create a GitHub issue)

---

## Documentation Principles

### 1. CURRENT + ARCHIVE Pattern

**Temporal documentation** (planning, feedback) uses two files:
- **CURRENT.md:** What's happening now (active work)
- **ARCHIVE.md:** What happened before (compressed history)

**Why:** Prevents file proliferation, clear temporal boundaries.

### 2. Single Source of Truth

**Reference documentation** uses single files:
- `why/RATIONALE.md` - All "why" questions
- `vision/FUTURE.md` - All future aspirations
- `.ai/MANIFEST.yaml` - All features and templates

**Why:** DRY principle, easy to find authoritative information.

### 3. Agent-First Organization

Every document answers:
- **WHO** can read/write this? (in YAML frontmatter)
- **WHEN** should it be consulted? (in index or frontmatter)
- **HOW** should it be updated? (managed_by field)

**Why:** LLMs are primary consumers, clarity improves agent performance.

### 4. Diataxis Alignment

| Quadrant | Our Docs | Purpose |
|:---|:---|:---|
| **Learning** | `guides/QUICKSTART.md` | Getting started tutorials |
| **Task-Oriented** | `guides/` | How-to guides for specific tasks |
| **Reference** | `architecture/CURRENT.md`, `research/` | Technical specifications |
| **Understanding** | `why/RATIONALE.md`, `vision/FUTURE.md` | Conceptual explanations |

---

## Contributing to Documentation

### Adding New Documentation

1. **Identify type:** Temporal (CURRENT/ARCHIVE) or Reference (single file)?
2. **Choose location:** Follow structure above
3. **Add YAML frontmatter:** Specify access rules
4. **Update this INDEX:** Add to appropriate section
5. **Cross-reference:** Link from related docs

### Updating Existing Documentation

1. **Check frontmatter:** Who can update? (`managed_by`)
2. **Follow patterns:** Match existing structure
3. **Update INDEX if needed:** If changing filenames or adding sections
4. **Maintain CURRENT + ARCHIVE:** Don't let CURRENT grow unbounded

### Templates

Templates defined in [`.ai/MANIFEST.yaml`](./.ai/MANIFEST.yaml):
- Guides (tutorials + how-to)
- Architecture documents
- Planning documents
- Feedback/audit reports
- ADRs (Architecture Decision Records)
- Rationale sections

---

## Project Context

**Project:** MAF Local (Hierarchical DevStudio)  
**Framework:** Microsoft Agent Framework (MAF SDK)  
**Philosophy:** FOSS-first, local-first, agent-driven development  
**Current Phase:** Phase 10.1 (MAF SDK Compliance Refactoring)

**For full project overview,** see main [`README.md`](../README.md) in project root.

---

## Questions?

- **Agents:** Consult `.ai/GUIDELINES.md` for coding standards and navigation shortcuts
- **Humans:** Open an issue or check `guides/` for help
- **Both:** See `why/RATIONALE.md` for conceptual understanding
