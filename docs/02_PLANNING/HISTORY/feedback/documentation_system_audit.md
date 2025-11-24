# Documentation System Audit: MAF SDK Alignment & Agent-Driven Workflows

**Date:** 2025-11-21  
**Auditor:** Assistant (on behalf of user)  
**Scope:** Holistic review of documentation architecture for agent workflow support

---

## Executive Summary

### Current State: ⚠️ **70% Complete**

**Strengths:**
- ✅ Clear temporal pattern (CURRENT + ARCHIVE) applied universally
- ✅ YAML frontmatter with access rules on all new docs
- ✅ Comprehensive templates in `.ai/MANIFEST.yaml`
- ✅ Agent role definitions in `.ai/agents.md`

**Critical Gaps:**
- ❌ No entry point from project root (`README.md` → `docs/`)
- ❌ No MAF SDK integration (governance, checkpointing for docs)
- ❌ No automated Documentation Agent workflow
- ❌ No Git/versioning integration strategy
- ❌ Templates exist but no tool enforcement

---

## Gap Analysis

### 1. Entry Point & Navigation (CRITICAL)

**Current State:**
- `docs/INDEX.md` exists and is comprehensive
- `README.md` (project root) has no link to documentation system
- Agents have no clear "start here" instruction

**Impact:** Agents and users don't know documentation system exists

**Recommendation:**
```markdown
# In README.md, add after "Quick Start" section:

## 📚 Documentation

This project follows an **agent-optimized documentation system**. 

- **For Humans:** Start at [`docs/INDEX.md`](./docs/INDEX.md)
- **For Agents:** Read [`.ai/GUIDELINES.md`](./docs/.ai/GUIDELINES.md) first, then use [`.ai/MANIFEST.yaml`](./docs/.ai/MANIFEST.yaml) for navigation shortcuts

**Quick Links:**
- [Current Phase](./docs/planning/CURRENT.md) - What's being worked on now
- [Architecture](./docs/architecture/CURRENT.md) - System design
- [Guides](./docs/guides/) - How-to documentation
```

**Priority:** 🔴 HIGH (1-2 hours)

---

### 2. Documentation Agent Design (MISSING)

**Current State:**
- `agents.md` defines `@docs-lead` role
- Lists tools: `plan_documentation_updates`, `get_update_template`
- **❌ These tools don't exist in codebase**

**Impact:** Documentation Agent cannot execute automated workflows

**Recommendation: Create Documentation Agent Infrastructure**

#### A. Create DocUpdatePlanner Tool
```python
# src/tools/doc_update_planner.py

from typing import List, Dict
from src.persistence.postgres import PostgresClient
import yaml

class DocUpdatePlanner:
    """Tool for Documentation Agent to determine what docs need updating."""
    
    def __init__(self, manifest_path: str, db: PostgresClient):
        with open(manifest_path) as f:
            self.manifest = yaml.safe_load(f)
        self.db = db
    
    async def get_affected_docs(self, feature_id: str) -> List[Dict]:
        """Returns list of docs that need updating for a feature."""
        feature = self.manifest['features'].get(feature_id)
        if not feature:
            return []
        
        affected = feature.get('affects', {})
        updates_needed = []
        
        for category, files in affected.items():
            for file_spec in files:
                updates_needed.append({
                    'path': file_spec['path'],
                    'change_type': file_spec['change'],
                    'description': file_spec['description'],
                    'template': self._get_template(file_spec['change'])
                })
        
        return updates_needed
    
    def _get_template(self, change_type: str) -> str:
        """Retrieves appropriate template from MANIFEST.yaml."""
        # Logic to extract template based on change_type
        pass
```

#### B. Integrate with MAF SDK Governance

**Problem:** Documentation changes are not tracked in governance DB

**Solution:**
```python
# Document updates should be logged like code changes

async def update_documentation(doc_path: str, content: str, reason: str):
    # 1. Update file
    with open(doc_path, 'w') as f:
        f.write(content)
    
    # 2. Log to Governance Agent
    decision = Decision(
        category="documentation_update",
        content={
            "path": doc_path,
            "reason": reason,
            "timestamp": datetime.utcnow(),
            "updated_by": "DocsLead"
        }
    )
    await governance_agent.store_decision(decision)
    
    # 3. (Optional) Commit to Git
    await artifact_manager.commit_to_git(
        files=[doc_path],
        message=f"docs: {reason}"
    )
```

**Priority:** 🟡 MEDIUM (4-6 hours)

---

###3. MAF SDK Alignment (PARTIAL)

**Current State:**
- ✅ YAML frontmatter mimics MAF SDK patterns
- ✅ Access rules documented
- ❌ No integration with MAF SDK `CheckpointStorage` for docs
- ❌ No integration with MAF SDK `AuditLogger`

**MAF SDK Patterns We Should Leverage:**

| MAF SDK Feature | Current Docs Usage | Recommended Integration |
|:---|:---|:---|
| **CheckpointStorage** | Not used | Snapshot `planning/CURRENT.md` state when phase starts/ends |
| **Governance Agent** | Not used | Log all doc updates (who, what, when) |
| **Context Providers** | Not used | Store doc embeddings in ChromaDB for semantic search |
| **Audit Logger** | Not used | Track doc access patterns (which agents read which docs) |

**Example: Checkpointing for Documentation**

```python
# When a phase starts
checkpoint = {
    "phase_id": "10.1",
    "planning_state": await read_file("planning/CURRENT.md"),
    "architecture_state": await read_file("architecture/CURRENT.md"),
    "timestamp": datetime.utcnow()
}
await checkpoint_storage.save("phase_10.1_start", checkpoint)

# When a phase ends (before archiving)
checkpoint = {
    "phase_id": "10.1",
    "planning_state": await read_file("planning/CURRENT.md"),
    "architecture_state": await read_file("architecture/CURRENT.md"),
    "changes_summary": "Refactored memory persistence layer",
    "timestamp": datetime.utcnow()
}
await checkpoint_storage.save("phase_10.1_end", checkpoint)
```

**Benefit:** Can revert docs to previous phase if needed (drift recovery)

**Priority:** 🟢 LOW (Future enhancement, not blocking)

---

### 4. Git/Versioning Integration (MISSING)

**Current State:**
- `agents.md` defines `@artifact-manager` with Git tools
- **❌ No documentation-specific versioning strategy**
- **❌ Unclear if agents should commit docs automatically**

**Problem:** Documentation updates happen in-memory but may not persist to Git

**Recommendation: Documentation Commit Strategy**

#### Option A: Automatic Commits (Aggressive)
```python
# Every doc update triggers immediate commit
await update_doc("planning/CURRENT.md", new_content)
await git_commit(
    files=["docs/planning/CURRENT.md"],
    message="docs(planning): update Phase 10.1 task status"
)
```

**Pros:** Full version history  
**Cons:** Noisy Git history

#### Option B: Batch Commits (Conservative)
```python
# Agent accumulates doc changes in session
session.pending_doc_updates.append("planning/CURRENT.md")
session.pending_doc_updates.append("architecture/CURRENT.md")

# At workflow checkpoint or phase boundary:
await git_commit(
    files=session.pending_doc_updates,
    message=f"docs: Phase {phase_id} updates"
)
```

**Pros:** Clean Git history  
**Cons:** Risk of losing intermediate changes

#### **Recommended: Option B** with checkpoint integration

**Priority:** 🟡 MEDIUM (2-3 hours to implement)

---

### 5. Cross-Cutting Concerns

**Question:** Does documentation system align with MAF SDK cross-cutting concerns?

| Concern | MAF SDK Implementation | Docs System Alignment | Status |
|:---|:---|:---|:---|
| **Auditing** | `AuditLogger` for all agent actions | Manual (no automatic tracking) | ❌ NOT ALIGNED |
| **Checkpointing** | `CheckpointStorage` for workflow state | Manual snapshots (none currently) | ❌ NOT ALIGNED |
| **Governance** | `GovernanceAgent` for decisions | YAML frontmatter (no DB persistence) | ⚠️ PARTIALLY ALIGNED |
| **Context Retrieval** | `ContextProvider` for memory | Docs not indexed in ChromaDB | ❌ NOT ALIGNED |
| **Permissions** | MAF SDK roles/tools | YAML `access` field (not enforced) | ⚠️ PARTIALLY ALIGNED |

**Recommendation: Middleware Layer for Documentation**

Create `src/middleware/doc_middleware.py`:

```python
from typing import List
from src.persistence.postgres import PostgresClient
from src.agents.governance_agent import GovernanceAgent

class DocumentationMiddleware:
    """Intercepts doc operations to enforce MAF SDK patterns."""
    
    def __init__(self, governance: GovernanceAgent, db: PostgresClient):
        self.governance = governance
        self.db = db
    
    async def read_doc(self, path: str, agent_id: str) -> str:
        """Read doc with audit logging."""
        # 1. Check access rules from YAML frontmatter
        frontmatter = self._parse_frontmatter(path)
        if not self._has_read_permission(agent_id, frontmatter):
            raise PermissionError(f"{agent_id} cannot read {path}")
        
        # 2. Log access
        await self.db.execute(
            "INSERT INTO doc_access_log (agent_id, doc_path, action, timestamp) "
            "VALUES ($1, $2, 'read', NOW())",
            agent_id, path
        )
        
        # 3. Return content
        with open(path) as f:
            return f.read()
    
    async def write_doc(self, path: str, content: str, agent_id: str, reason: str):
        """Write doc with governance logging."""
        # 1. Check write permission
        frontmatter = self._parse_frontmatter(path)
        if not self._has_write_permission(agent_id, frontmatter):
            raise PermissionError(f"{agent_id} cannot write to {path}")
        
        # 2. Update file
        with open(path, 'w') as f:
            f.write(content)
        
        # 3. Log to governance
        decision = {
            "type": "documentation_update",
            "path": path,
            "agent": agent_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.governance.store_decision(decision)
        
        # 4. Audit log
        await self.db.execute(
            "INSERT INTO doc_access_log (agent_id, doc_path, action, timestamp) "
            "VALUES ($1, $2, 'write', NOW())",
            agent_id, path
        )
```

**Benefit:** Enforces permissions, provides audit trail, integrates with MAF SDK governance

**Priority:** 🟡 MEDIUM (3-4 hours)

---

## Recommendations Summary

### Immediate (Next 2-4 hours)
1. ✅ **Update README.md** with link to docs system (1 hour)
2. ✅ **Fix remaining cross-references** (CURRENT_STATE.md → CURRENT.md) (1 hour)
3. ✅ **Create Documentation Update Workflow guide** in `docs/guides/` (2 hours)

### Short-Term (Next Sprint)
4. 🟡 **Implement DocUpdatePlanner tool** (4-6 hours)
5. 🟡 **Create DocumentationMiddleware** for permissions + auditing (3-4 hours)
6. 🟡 **Define Git commit strategy** for doc updates (2-3 hours)

### Medium-Term (Phase 11+)
7. 🟢 **Index docs in ChromaDB** for semantic search (2-3 hours)
8. 🟢 **Integrate CheckpointStorage** for phase boundary snapshots (2 hours)
9. 🟢 **Build Documentation Agent** as full MAF SDK agent (8-12 hours)

---

## Is This System Generic/Reusable?

### ✅ **Yes, with modifications:**

**What's Generic:**
- CURRENT + ARCHIVE temporal pattern
- YAML frontmatter for access rules
- Diataxis-aligned structure (guides, why, architecture, planning)
- `.ai/` folder pattern for agent config

**What's Project-Specific:**
- `.ai/MANIFEST.yaml` feature tracking (needs to be recreated per project)
- Specific file names/paths (but pattern is reusable)
- Agent roles in `agents.md` (would differ by project type)

**To Make Fully Generic:**
1. Create `docs-system-template/` repo with structure
2. Include initialization script: `init_docs.sh <project_name>`
3. Parameterize MANIFEST.yaml generation
4. Provide agent role templates for different project types (web app, CLI tool, library)

---

## Final Assessment

| Criterium | Score | Notes |
|:---|:---:|:---|
| **Entry Point Clarity** | 3/10 | No README link, agents don't know system exists |
| **Agent Workflow Support** | 5/10 | Templates exist, tools don't |
| **MAF SDK Alignment** | 4/10 | Patterns match philosophically but no integration |
| **Permission Enforcement** | 2/10 | YAML rules documented but not enforced |
| **Versioning Strategy** | 1/10 | No Git integration |
| **Generic/Reusable** | 7/10 | Pattern is great, needs templatization |
| **Cross-Cutting Concerns** | 3/10 | Missing auditing, checkpointing, governance integration |

**Overall Readiness: 70%** ⚠️

**Blockers for Documentation Agent:**
1. No DocUpdatePlanner tool implementation
2. No permission enforcement layer
3. No governance integration

**Blockers for Versioning Agent:**
1. No Git commit strategy defined
2. No artifact manager integration for docs
3. No drift detection between Git history and current state

---

## Next Steps (Recommendation)

**If proceeding immediately to Phase 10 MAF SDK work:**
- Defer full Documentation Agent until Phase 11
- Manually manage docs for Phase 10
- Keep current structure (it's functional, just not automated)

**If prioritizing documentation automation:**
1. Implement README entry point (30 min)
2. Create DocUpdatePlanner tool (4 hours)
3. Build DocumentationMiddleware (3 hours)
4. Wire into MAF SDK governance (2 hours)
5. **THEN** proceed to Phase 10

**My Recommendation:** Option 1 (defer). The foundation is solid. Automation can wait until we prove the pattern works manually first.
