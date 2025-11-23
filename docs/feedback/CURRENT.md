---
access: read-write
audience: agents | humans
update_trigger: audit_conducted | feedback_received
managed_by: Agents and humans
---

# Feedback: CURRENT

**Last Updated:** 2025-11-23

## Active Issues

### 1. Limited Tool Set ⚠️

**Status:** Known Limitation  
**Severity:** Low  
**Category:** Feature Gap

**Issue:** Current tool set is minimal (write_file, execute_code). No advanced development tools.

**Impact:** Agents can create files but cannot analyze code quality, run tests, or perform deployments.

**Recommendation:** Add incrementally in future phases:
- Code analysis tools (linting, complexity)
- Testing tools (pytest execution, coverage)
- Deployment tools (Docker, Git integration)

---

### 2. Database Tables Missing ⚠️

**Status:** Known Limitation  
**Severity:** Low  
**Category:** Infrastructure

**Issue:** UI shows errors for missing `projects` and `sessions` tables in PostgreSQL.

**Impact:** Sidebar features don't work (project list, session history). Core chat functionality unaffected.

**Recommendation:** Add database migrations in next infrastructure phase.

---

### 3. Single-Tier Delegation 📊

**Status:** Architectural Decision  
**Severity:** N/A  
**Category:** Design Trade-off

**Issue:** Only Liaison → ProjectLead hierarchy. No Domain Leads or Executors.

**Rationale:** MVP-first approach - prove core execution works before adding complexity.

**Plan:** Reintroduce multi-tier architecture incrementally with proper MAF Workflow orchestration.

---

## Resolved Issues (Moved to ARCHIVE)

### ✅ Tool Execution Fixed (2025-11-23)
- **Issue:** LiteLLM client couldn't parse tool calls
- **Resolution:** Refactored to extend `BaseChatClient` with `@use_function_invocation`
- **Archived:** See feedback/ARCHIVE.md - Emergency Refactor Complete

### ✅ File Generation Operational (2025-11-23)
- **Issue:** No secure file writing capability
- **Resolution:** Implemented sandboxed `write_file` tool with path validation
- **Archived:** See feedback/ARCHIVE.md - Emergency Refactor Complete

### ✅ Architecture Simplified (2025-11-23)
- **Issue:** Complex hierarchy with no working implementation
- **Resolution:** Deleted unused agents, focused on 2-tier MVP
- **Archived:** See feedback/ARCHIVE.md - Emergency Refactor Complete

---

## Update Guidelines

When adding new feedback:
1. Create a new section under "Active Issues"
2. Include: Status, Severity, Category, Issue, Impact, Recommendation
3. When resolved, move to ARCHIVE.md with resolution details
