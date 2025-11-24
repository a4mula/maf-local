# Documentation Systems Research

**Date:** November 21, 2025  
**Purpose:** Research how established systems structure documentation for both humans and AI agents.

---

## Executive Summary

After researching VS Code, GitHub Copilot, CrewAI, Google Engineering, and the Diataxis framework, a clear pattern emerges: **The most effective documentation systems use the Diataxis 4-quadrant model** (Tutorials, How-To Guides, Reference, Explanation) combined with **AI-optimized metadata and indexing**.

### Key Findings

1. **Diataxis is the industry standard** for organizing technical documentation
2. **GitHub Copilot** uses special files (`copilot-instructions.md`, `agents.md`) for AI context
3. **Google** treats docs as code: version control, reviews, ownership, and style guides
4. **CrewAI** structures agent docs with clear role/goal/tool separation
5. **VS Code** organizes by user journey: Getting Started → Features → Customization

---

## The Diataxis Framework (Recommended)

Diataxis divides documentation into **4 types** based on user intent:

| Type | Purpose | Audience | Format |
| :--- | :--- | :--- | :--- |
| **Tutorials** | Learning by doing | Beginners | Step-by-step, concrete goals |
| **How-To Guides** | Solve specific problems | Practitioners | Task-focused, recipes |
| **Reference** | Look up facts | All levels | Technical specs, API docs |
| **Explanation** | Understand concepts | All levels | Conceptual, discursive |

### Why This Works for DevStudio

- **Agents**: Can quickly identify document type and extract relevant info
- **Humans**: Can navigate based on current need (learning vs. lookup)
- **Maintainability**: Clear boundaries prevent content bleed

---

## GitHub Copilot Workspace Approach

GitHub uses **special index files** to guide AI agents:

### 1. `copilot-instructions.md`
- **Purpose**: Central repository of prompts, guidelines, and standards
- **Content**: Common patterns, coding conventions, project-specific rules
- **Location**: Project root

### 2. `agents.md`
- **Purpose**: Define custom agent personas
- **Content**:
  - Agent role and tech stack knowledge
  - Project structure overview
  - Executable commands and workflows
  - Boundaries (what the agent should/shouldn't do)

### 3. Well-Scoped Issues
- Issues function as AI prompts
- Include: problem description, acceptance criteria, affected files

### Why This Works for DevStudio

- **Project Isolation**: Each project gets its own `copilot-instructions.md`
- **Agent Specialization**: `agents.md` defines domain-specific agents
- **Task-Oriented**: Maps naturally to MAF's hierarchical agent structure

---

## Google Engineering Practices

### Documentation as Code

| Principle | Implementation |
| :--- | :--- |
| **Ownership** | Every doc has a clear owner/maintainer |
| **Review Process** | Technical review → Audience review → Style review |
| **Version Control** | Docs tracked in Git alongside code |
| **Freshness** | Regular audits to ensure accuracy |
| **Style Guide** | Enforced consistency (Google Developer Style Guide) |

### Documentation Types at Google

1. **Reference**: API docs, code comments
2. **Design Docs**: Architectural decisions, proposals
3. **Tutorials**: Step-by-step learning paths

### Why This Works for DevStudio

- **Single Source of Truth**: Docs live with code
- **Quality Gates**: Reviews ensure accuracy
- **Discoverability**: Consistent style makes docs predictable

---

## CrewAI Documentation Structure

CrewAI uses a **role-based hierarchy** for agent docs:

```
docs/
├── introduction/       # Overview, concepts
├── installation/       # Setup guides
├── quickstart/         # First crew tutorial
├── agents/             # Agent framework (DETAILED)
│   ├── overview.md
│   ├── attributes.md
│   ├── tools.md
│   └── examples.md
├── flows/              # Orchestration
└── api-reference/      # Technical specs
```

### Key Insight: Agent Documentation is Primary

For an agent framework, **agent documentation gets its own top-level section** with deep detail on:
- Agent attributes (role, goal, backstory)
- Tools and capabilities
- Memory and context management
- Collaboration patterns

---

## Proposed DevStudio Documentation Architecture

### Directory Structure

```
docs/
├── README.md                         # Entry point, quick links
│
├── .ai/                              # AGENT WORKSPACE
│   ├── copilot-instructions.md       # Project-level guidelines (GitHub pattern)
│   ├── agents.md                     # Agent persona definitions
│   ├── feature_manifest.yaml         # Feature → Docs mapping (NEW)
│   ├── update_templates.yaml         # Doc update templates (NEW)
│   └── doc_graph.json                # Dependency graph (NEW)
│
├── tutorials/                        # LEARNING-ORIENTED (Diataxis)
│   ├── 01_quickstart.md
│   ├── 02_first_project.md
│   └── 03_custom_agent.md
│
├── how-to/                           # PROBLEM-ORIENTED (Diataxis)
│   ├── setup_gpu_acceleration.md
│   ├── add_new_tool.md
│   ├── configure_litellm.md
│   └── run_migrations.md
│
├── reference/                        # INFORMATION-ORIENTED (Diataxis)
│   ├── api/                          # API specs
│   │   ├── agent_api.md
│   │   └── project_api.md
│   ├── architecture/                 # System design
│   │   ├── current_state.md
│   │   └── data_flow.md
│   └── agents/                       # Agent specs (CrewAI pattern)
│       ├── liaison_agent.md
│       ├── project_lead_agent.md
│       └── domain_lead_agent.md
│
├── explanation/                      # UNDERSTANDING-ORIENTED (Diataxis)
│   ├── why_hierarchical_agents.md
│   ├── governance_model.md
│   └── phase_10_pivot.md
│
└── planning/                         # INTERNAL ONLY (Google pattern)
    ├── roadmap.md                    # Phase tracker
    ├── phase_planner.md              # Historical phases
    └── implementation_plan.md        # Current work
```

### The `.ai/` Agent Workspace (NEW)

This directory contains **machine-readable metadata** to help agents efficiently update documentation.

#### 1. `feature_manifest.yaml`
Maps features/phases to affected documents:

```yaml
features:
  multi_project_support:
    status: planned
    phase: 10
    affects:
      tutorials:
        - path: tutorials/01_quickstart.md
          change: add_step
          description: "Add project selection step"
      how_to:
        - path: how-to/create_project.md
          change: create_new
      reference:
        - path: reference/api/project_api.md
          change: create_new
```

#### 2. `update_templates.yaml`
Defines how to update each doc type:

```yaml
tutorial:
  add_step:
    template: |
      ## Step {step_number}: {title}
      
      {instructions}
      
      ```{language}
      {code_example}
      ```

how_to:
  create_new:
    template_file: "templates/how-to-template.md"
```

#### 3. `doc_graph.json`
Machine-readable dependency graph:

```json
{
  "reference/api/project_api.md": {
    "depends_on": ["reference/architecture/current_state.md"],
    "referenced_by": ["how-to/create_project.md"]
  }
}
```

### Metadata and Indexing

#### Frontmatter (YAML)

Every doc includes:

```yaml
---
type: tutorial | how-to | reference | explanation
audience: beginner | practitioner | advanced
status: draft | review | published
last_updated: 2025-11-21
related:
  - api/agent_api.md
  - agents/liaison_agent.md
tags: [agents, api, setup]
feature_refs: [multi_project_support]  # NEW: Links to feature_manifest
---
```

#### AI Optimization

1. **Structured Headers**: Consistent H1 → H2 → H3 hierarchy
2. **Code Fences**: Always specify language for syntax highlighting
3. **Tables**: For comparative data (ports, services, phases)
4. **Callouts**: Use alerts for warnings, tips, important notes
5. **Links**: Absolute paths to related docs
6. **Feature Tags**: Connect docs to features in manifest

---

## Implementation Checklist

### Phase 1: Restructure Existing Docs

- [ ] Create `docs/.ai/` directory
- [ ] Write `copilot-instructions.md` (project guidelines)
- [ ] Write `agents.md` (agent personas)
- [ ] Migrate existing docs to Diataxis structure:
  - [ ] Move `Phase_Planner.md` → `planning/roadmap.md`
  - [ ] Move `CURRENT_STATE.md` → `reference/architecture/current_state.md`
  - [ ] Move `Ideal State.md` → `explanation/vision.md`
- [ ] Create missing categories:
  - [ ] `tutorials/01_quickstart.md`
  - [ ] `how-to/` directory with common tasks
  - [ ] `reference/api/` for endpoint docs

### Phase 2: Add Metadata

- [ ] Add YAML frontmatter to all docs
- [ ] Create `docs/index.json` (machine-readable manifest)
- [ ] Generate docs graph (related documents map)

### Phase 3: Tooling

- [ ] Create `FileTreeReader` tool for agents
- [ ] Create `DocsFetcher` tool (reads by type/tag)
- [ ] Update `ContextRetrievalAgent` to use Diataxis structure

---

## Benefits for DevStudio

1. **Agent Introspection**: Agents can quickly find relevant info by type
2. **Replicability**: Every project follows the same structure
3. **Scalability**: Clear boundaries make it easy to add new docs
4. **Human + AI**: Works for both audiences simultaneously
5. **Industry Standard**: Diataxis is widely adopted and understood

---

## References

- [Diataxis Framework](https://diataxis.fr/)
- [Google Developer Style Guide](https://developers.google.com/style)
- [GitHub Copilot Workspace Best Practices](https://github.blog/)
- [CrewAI Documentation](https://docs.crewai.com/)
