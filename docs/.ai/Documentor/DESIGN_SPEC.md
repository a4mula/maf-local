# Documentor Agent – Design Specification

**Location:** `docs/.ai/Documentor/DESIGN_SPEC.md`

---

## 1. Purpose & Scope
The Documentor agent is a **technical poet** that consumes a **SESSION_HANDOFF.md** produced by the Implementation Agent (Gemini 3 Pro) and automatically brings the entire `docs/` tree up‑to‑date.  It must:
- Parse the handoff into discrete actions (add, modify, delete). 
- Apply those actions to the appropriate documentation files (architecture, planning, guides, meta‑docs). 
- Resolve conflicts with existing content in a deterministic way.
- Emit a concise audit checklist and commit the changes.
- Operate under the Antigravity umbrella, coordinating with the Project Lead (Claude 4.5) and the Execution Engine (Gemini 3 Pro).

---

## 2. Core Responsibilities
| Responsibility | Description |
|----------------|-------------|
| **Ingestion** | Read `docs/.ai/Documentor/SESSION_HANDOFF.md` (or a path supplied via CLI). |
| **Parsing** | Detect top‑level sections (`## New Directories & Files`, `## Modified Files`, `## Architecture & Relationships`, etc.). Extract markdown tables, mermaid blocks, and free‑form notes. |
| **Mapping** | Translate each entry to a target file path inside `docs/`. Use a configurable mapping table (e.g., `Architecture → docs/architecture/CURRENT.md`). |
| **Update Rules** | *Add*: create missing files/directories. *Modify*: replace specific sections (identified by header or marker comment). *Delete*: remove deprecated files (rare, gated by a `# DEPRECATED` comment). |
| **Conflict Detection** | Before writing, compare the existing file’s hash with the version stored in the handoff. If they differ, flag a conflict. |
| **Conflict Resolution** | - **Auto‑merge** when changes are non‑overlapping (different headers). 
- **Prompt** the user (or Project Lead) for manual merge when overlapping. |
| **Commit & Audit** | After successful updates, generate `docs_audit_checklist.md` entries and stage a git commit with a standardized message (`"doc: apply SESSION_HANDOFF <date>"`). |
| **Reporting** | Emit a short JSON summary to stdout and optionally write `docs/.ai/Documentor/REPORT.json`. |

---

## 3. Ingestion & Parsing Details
1. **File Detection** – The agent looks for `SESSION_HANDOFF.md` in the configured directory. If not found, it exits with a non‑zero status.
2. **Section Extraction** – Uses a regex `^##\s+(.*)$` to capture section titles. The body of each section is trimmed and stored.
3. **Special Sections**:
   - **Architecture & Relationships** – Contains a Mermaid diagram. The agent extracts the block between ````mermaid` and ```` and replaces the first Mermaid block in `docs/architecture/CURRENT.md`.
   - **New Directories & Files** – Table with columns `Path` and `Description`. For each row, the agent creates the directory (if missing) and writes a placeholder file with the description.
   - **Modified Files** – Table with `Path` and `Change Description`. The agent loads the target file, searches for a marker comment `<!-- Documentor Update -->` (inserts if missing), and appends the description under that marker.
4. **Markdown Sanitisation** – Strips trailing whitespace, normalises line endings, and validates that any code fences have a language spec.

---

## 4. Update Rules & Conflict Handling
### 4.1 Additions
- **Directories**: `os.makedirs(path, exist_ok=True)`.
- **Files**: Write the supplied description as a top‑level header, then insert a marker comment.

### 4.2 Modifications
- Locate the **first header** that matches the `Change Description` title (or the marker comment).
- If the header exists, replace the block between the header and the next header with the new content.
- If the header does **not** exist, append a new section at the end of the file.

### 4.3 Deletions (rare)
- Only performed when the handoff includes a `# DEPRECATED` flag.
- The agent moves the file to `docs/.archive/` and records the move in the audit checklist.

### 4.4 Conflict Detection Algorithm
```text
1. Compute SHA‑256 of the current file.
2. Compare with the hash stored in the handoff (if provided).
3. If hashes match → safe to apply.
4. If mismatch → generate a conflict entry:
   - file path
   - diff (using difflib)
   - status = "conflict"
5. Return conflict list to the caller.
```
If any conflicts exist, the agent **halts** and writes `REPORT.json` with a `needs_review: true` flag.

### 4.5 Resolution Strategies
- **Auto‑merge** when the conflicting sections are disjoint (different header IDs). The agent merges the non‑overlapping parts.
- **User Review** – The agent prints a concise list of conflicted files and asks the Project Lead (Claude 4.5) to approve a manual merge. This can be done via a generated PR or a CLI prompt.

---

## 5. Integration Points
| Component | Interaction Mode |
|-----------|------------------|
| **Gemini 3 Pro (Implementation Agent)** | Calls `documentor.py apply --handoff <path>` after it finishes a phase. The handoff file is the sole input. |
| **Claude 4.5 (Project Lead)** | Reads `docs/.ai/Documentor/REPORT.json` to see success/failure and decides whether to proceed to the next phase. |
| **CI/CD Pipeline** | Runs `documentor.py verify` on every push to ensure docs are consistent with the latest handoff. |
| **Git Hooks** | Pre‑commit hook runs a lightweight lint of the handoff and a dry‑run of the Documentor (no writes). |

---

## 6. CI / Automation Hooks
1. **Pre‑commit** (`.pre-commit-config.yaml`):
   - `documentor.py lint --handoff docs/.ai/Documentor/SESSION_HANDOFF.md`
   - `markdownlint` on the entire `docs/` tree.
2. **Post‑merge** job:
   - Execute `documentor.py apply --handoff <latest>`.
   - If conflicts → fail the job and post a comment on the PR with `REPORT.json`.
3. **Scheduled Audits** (daily):
   - Run `documentor.py audit` to generate an updated `docs_audit_checklist.md` and compare with the previous version.
4. **GitHub Action** example:
```yaml
name: Docs Update
on: [push]
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m src.tools.documentor apply --handoff docs/.ai/Documentor/SESSION_HANDOFF.md
```

---

## 7. Security & Permissions
- The agent runs with **read‑write** access only inside the `docs/` directory (enforced via `pathlib.Path.resolve()` and a whitelist check).
- All writes are logged to `logs/documentor.log` with timestamps, user (git author), and SHA‑256 of the before/after files.
- The handoff file must be signed (optional) – a simple SHA‑256 checksum can be stored alongside the file and verified before processing.

---

## 8. Extensibility
- **Plugin System** – Future sections (e.g., `## New API Endpoints`) can be handled by plug‑in modules placed under `src/tools/documentor/plugins/`.
- **Output Formats** – Besides markdown, the agent can emit **reStructuredText** or **HTML** by toggling a CLI flag.
- **Multi‑Project Support** – The same engine can be pointed at another repository by passing `--root /path/to/other/docs`.

---

## 9. Example CLI Usage
```bash
# Apply a new handoff (writes files)
python -m src.tools.documentor apply --handoff docs/.ai/Documentor/SESSION_HANDOFF.md

# Dry‑run – only shows what would change
python -m src.tools.documentor apply --handoff docs/.ai/Documentor/SESSION_HANDOFF.md --dry-run

# Lint the handoff for structural errors
python -m src.tools.documentor lint --handoff docs/.ai/Documentor/SESSION_HANDOFF.md
```

---

## 10. Acceptance Criteria
- ✅ The agent can ingest a handoff containing at least one new file, one modified file, and a Mermaid diagram.
- ✅ All changes are reflected in the appropriate docs without manual editing.
- ✅ Conflicts are detected and reported in `REPORT.json`.
- ✅ CI pipeline passes when the handoff is clean and fails with a helpful error when conflicts exist.
- ✅ A concise audit checklist (`docs_audit_checklist.md`) is automatically updated.

---

*Prepared by the Antigravity Documentor design team on 2025‑11‑24.*
