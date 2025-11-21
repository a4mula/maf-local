---
access: read-only
audience: agents | humans
update_trigger: feedback_resolved
managed_by: Agents (compression from CURRENT.md)
---

# Feedback: ARCHIVE

> [!NOTE]
> This document contains **summarized history** of resolved feedback, audits, and retrospectives.  
> Active feedback lives in [`CURRENT.md`](./CURRENT.md).

---

## Phase 9: Docker Formalization (Resolved 2025-11-15)

**Type:** Post-Implementation Review  
**Finding:** Container networking complexity required multiple iterations

**Resolution:**
- Documented service names in `docker-compose.yaml`
- Created troubleshooting guide in `guides/DEPLOYMENT.md`
- Added networking diagram to `architecture/CURRENT.md`

**Outcome:** ✅ One-click deployment achieved via `start_node.sh`

---

## Phase 8: UI Integration (Resolved 2025-11-10)

**Type:** Integration Audit  
**Finding:** Streamlit and Next.js had disconnected state

**Resolution:**
- Created unified `/api/agent_api.py` backend
- Implemented WebSocket for real-time agent status
- Added state synchronization layer

**Outcome:** ✅ Both UIs now reflect real-time agent activity

---

## Phase 7: Metrics Collection (Resolved 2025-11-05)

**Type:** Performance Audit  
**Finding:** Custom metrics not properly exposed to Prometheus

**Resolution:**
- Fixed metrics endpoint in `src/services/metrics_service.py`
- Updated Prometheus scrape config
- Created Grafana dashboards

**Outcome:** ✅ Full observability achieved

---

## Early Phase Feedback (Phases 1-6)

### Agent Hierarchy (Phase 1)
- **Issue:** Initial escalation paths unclear
- **Resolution:** Documented tier responsibilities in `AGENTS.md`

### Governance Layer (Phase 2)
- **Issue:** Drift detection false positives
- **Resolution:** Improved YAML schema validation

### Checkpointing (Phase 3)
- **Issue:** Checkpoint serialization errors
- **Resolution:** Implemented proper `to_dict()`/`from_dict()` methods

### Context Management (Phase 4)
- **Issue:** ChromaDB collection naming conflicts
- **Resolution:** Scoped collections by agent type

### Artifact Management (Phase 5)
- **Issue:** Git commits lacked context
- **Resolution:** Added structured commit message templates

### Provider Discovery (Phase 6)
- **Issue:** LiteLLM authentication failures
- **Resolution:** Added `LITELLM_MASTER_KEY` to `.env` template

---

## Template: Adding Resolved Feedback

When moving feedback from CURRENT.md to ARCHIVE.md, use this format:

```markdown
## [Phase X]: [Topic] (Resolved YYYY-MM-DD)

**Type:** Audit | Retrospective | Post-Mortem  
**Finding:** [Brief description of issue]

**Resolution:**
- [Action taken 1]
- [Action taken 2]

**Outcome:** ✅ [Final state or metric]
```

**Keep summaries concise** - Detailed documentation lives in guides, architecture docs, or implementation plans.
