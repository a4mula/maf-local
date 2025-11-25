# SRC Domain Audit Report

**Date:** 2025-11-24
**Auditor:** SRC Agent (Gemini 3 Pro)
**Plan ID:** SRC-AUDIT-001

---

## Executive Summary
The `maf-local` codebase is in a **healthy state** (Score: 8.5/10), successfully implementing the 4-tier UBE architecture with strict separation of concerns. The directory structure logically maps to the agent hierarchy, and test coverage is robust across unit and integration levels.

**Key Strengths:**
- **Architectural Clarity:** `src/agents/` structure perfectly mirrors the Tier 1-4 hierarchy.
- **Test Coverage:** Comprehensive suite (44 tests) covering all core components.
- **MAF Compliance:** Pure usage of `@ai_function` and `ChatAgent` primitives.

**Primary Areas for Improvement:**
- **Tool Organization:** `src/tools/` is a flat list that doesn't reflect tier-based access control.
- **Verification Scripts:** `tests/verification/` contains executable scripts mixed with test logic.
- **Context Loading:** `ProjectLeadAgent` contains repetitive, hardcoded context loading logic.

---

## 1. Code Organization Analysis

### 1.1 Directory Structure Effectiveness
- **src/ (15 subdirs):** Well-organized. `agents/`, `workflows/`, `models/`, `persistence/` provide clear separation.
- **tests/ (3 subdirs):** `unit/` and `integration/` are standard. `verification/` is non-standard (see 3.3).
- **Observation:** `src/tools/` is becoming crowded (9 files).

### 1.2 Module Cohesion & Coupling
- **Cohesion:** High. Agents focus on their specific tier responsibilities.
- **Coupling:** Low. Communication is mediated via Workflows (`OLBWorkflow`, `TLBWorkflow`) and Data Contracts (`StrategicPlan`), preventing direct agent-to-agent coupling.

### 1.3 Naming Conventions
- **Consistency:** Excellent. `*_agent.py`, `*_workflow.py`, `*_executor.py`.
- **Clarity:** Names are self-documenting (e.g., `dev_domain_lead.py`).
- **Minor Issue:** `code_tools.py` vs `coder_executor.py` (noun vs agent role).

---

## 2. Architectural Alignment

### 2.1 Agent Hierarchy Mapping
The file structure perfectly supports the 4-Tier UBE:
- **Tier 1:** `src/agents/liaison_agent.py`
- **Tier 2:** `src/agents/project_lead_agent.py`
- **Tier 3:** `src/agents/domain_leads/`
- **Tier 4:** `src/agents/executors/`

### 2.2 Workflow Integration
- Workflows are centralized in `src/workflows/`.
- `olb_workflow.py` (Tier 2→3) and `tlb_workflow.py` (Tier 3→4) are clearly named and located.

### 2.3 Tool Organization
- **Current:** Flat list in `src/tools/`.
- **Issue:** Hard to distinguish which tools belong to which agent tier. `ALL_TOOLS` import in `ProjectLeadAgent` suggests broad access, which might violate PoLA if not carefully managed by `PermissionFilter`.

---

## 3. Test Suite Organization

### 3.1 Test Coverage Mapping
- **Unit:** Strong coverage for agents, workflows, and persistence.
- **Integration:** Covers key flows (`phase1_integration`, `full_hierarchy`).
- **Gaps:** `QADomainLead` (planned) obviously has no tests yet.

### 3.2 Test Quality Assessment
- **Clarity:** Test names are descriptive (`test_olb_workflow.py`).
- **Independence:** Tests use fixtures and mocks effectively.

### 3.3 Test Execution Patterns
- **Issue:** `tests/verification/` contains scripts like `verify_phase2_governance.py` that seem to be "run-once" verification scripts rather than persistent regression tests. They clutter the test suite.

---

## 4. Dependency Analysis

### 4.1 Internal Dependencies
- **Graph:** Agents → Workflows → Models. Clean unidirectional flow.
- **Circular Deps:** None detected.

### 4.2 External Dependencies
- **requirements.txt:** 19 packages.
- **Issue:** **No version pinning**. `pydantic`, `fastapi`, `streamlit` are unpinned, posing a risk of breaking changes in future installs.

### 4.3 MAF SDK Compliance
- **Status:** 100% Compliant.
- **Evidence:** `ProjectLeadAgent` uses `@ai_function` for `submit_strategic_plan`. No legacy `UniversalTool` usage found.

---

## 5. Code Quality Metrics

### 5.1 Complexity Analysis
- **ProjectLeadAgent:** Context loading logic (lines 17-49) is repetitive and brittle (hardcoded paths).
- **OLBWorkflow:** `execute_plan` is clean but relies on sequential execution (MVP limitation).

### 5.2 Documentation Quality
- **Docstrings:** Present and Google-style compliant in inspected files.
- **READMEs:** `src/` subdirectories generally lack READMEs explaining their specific purpose.

### 5.3 Error Handling
- **Pattern:** `try/except` blocks present in critical paths (e.g., `OLBWorkflow` task execution).
- **Logging:** Basic `print()` statements used. Should migrate to structured logging.

---

## Recommendations

### High Priority
1. **Pin Dependencies:** Update `requirements.txt` with specific versions to ensure reproducibility.
2. **Refactor Context Loading:** Extract `ProjectLeadAgent` context loading into a `ContextService` or utility to remove hardcoded paths and duplication.
3. **Restructure Tools:** Group tools by tier (e.g., `src/tools/tier1`, `src/tools/tier4`) to enforce PoLA visually and structurally.

### Medium Priority
1. **Standardize Logging:** Replace `print()` with a proper logger (`src.utils.logger`) for better observability.
2. **Clean Up Verification:** Move `tests/verification/` scripts to `scripts/verification/` or convert them to standard pytest integration tests.
3. **Add Subdirectory READMEs:** Add `README.md` to `src/agents/`, `src/workflows/` explaining the tier responsibilities.

### Low Priority
1. **Rename Code Tools:** Rename `code_tools.py` to `coder_tools.py` to match `CoderExecutor`.

---

## Technical Debt Identified
*For DOCS Agent Research Tasks*

1. **Dependency Management:** Lack of version pinning in `requirements.txt`.
2. **Hardcoded Paths:** `ProjectLeadAgent` relies on `/app/project_root` and fallback paths.
3. **Logging:** Use of `print` statements instead of structured logging.
4. **Test Organization:** Mixing of verification scripts with regression tests.
5. **Tool Flatness:** Lack of hierarchy in `src/tools/`.
