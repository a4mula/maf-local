# Strategic Architecture Review: MAF Studio Deployment

**Date:** November 22, 2025
**Status:** Draft / Proposal
**Author:** Antigravity (Agent)

## 1. Executive Summary

The user has identified a critical friction point in the current "Monolithic Container" architecture: **Docker is acting as a barrier rather than an enabler.**

By attempting to containerize the entire IDE (UI + Agent) and mount the host's filesystem into it, we have created a fragile environment where:
1.  **Path Mismatches**: `/workspaces` vs. `/home/user/projects` causes confusion.
2.  **Permission Issues**: Docker root vs. Host user permissions lead to "Failed to create project" errors.
3.  **Lack of Isolation**: All projects share the same runtime environment (dependencies) inside the single agent container.

This deviates from the "IDE" mental model (VS Code, Antigravity) where the tool seamlessly interacts with the host environment.

## 2. Architectural Models Comparison

We evaluated three approaches against the goal of a "Holistic, IDE-like Experience".

### Model A: Monolithic Container (Current)
*   **Architecture**: UI, Agent, DB, Ollama all in Docker. Host projects mounted via volumes.
*   **Pros**: Single `docker-compose up` command.
*   **Cons**:
    *   **Friction**: "Restart to add folder".
    *   **Permissions**: Constant battle with UID/GID.
    *   **Abstraction Leak**: User has to know about Docker volume mappings.
*   **Verdict**: **Untenable for a smooth IDE experience.**

### Model B: Container-Per-Project (VS Code Dev Containers)
*   **Architecture**: DevStudio (UI) spawns a *new* container for each project.
*   **Pros**: Perfect isolation. "DevStudio as a Service".
*   **Cons**: High complexity (Docker-in-Docker orchestration). Overkill for a "Local Studio" phase.
*   **Verdict**: **Ideal Long-Term Goal (Phase 15+)**, but too complex for now.

### Model C: Host-Native Runtime (Hybrid) - **RECOMMENDED**
*   **Architecture**:
    *   **Infrastructure**: Postgres, Ollama, Chroma run in Docker (stable, hard-to-install deps).
    *   **Runtime**: Streamlit UI and Agent run **natively on the Host** (in a Python venv).
*   **Pros**:
    *   **Native Access**: Agent sees `/home/robb/projects` exactly as you do. No mounts needed.
    *   **Zero Permission Issues**: Runs as your user.
    *   **Performance**: No filesystem bridge overhead.
    *   **Simplicity**: "It just works" with local tools (git, compilers).
*   **Cons**: Requires local Python setup (solved via script).

## 3. The "Better Approach": Pivot to Host-Native Runtime

To align with the vision of "DevStudio interfaces with that project wherever it resides", we should **stop fighting Docker**.

### Proposed Changes

1.  **Slim Down Docker Compose**:
    *   Remove `maf-ui` and `maf-agent` services.
    *   Keep `maf-postgres`, `maf-ollama`, `maf-chroma`.
    *   Expose ports (`5432`, `11434`, `8000`) to localhost.

2.  **Create `run_studio.sh`**:
    *   Checks for Python 3.12+.
    *   Creates/Activates a local `.venv`.
    *   Installs `requirements.txt`.
    *   Launches Streamlit and Agent processes on the host.

3.  **Config Update**:
    *   Update `.env` to point to `localhost` ports instead of Docker DNS names.

### Comparison to Antigravity / VS Code
*   **VS Code**: Runs on host. Connects to local files. Uses Docker only when requested (Dev Containers).
*   **Antigravity**: Runs as a process. Accesses files directly.
*   **MAF Studio (New)**: Will run on host. Accesses files directly. Uses Docker for "backend services" only.

## 4. Roadmap to Pivot

1.  **Phase 10.2 (Refactor)**:
    *   Update `docker-compose.yaml` (Infrastructure only).
    *   Create `start_host.sh` script.
    *   Update `settings.py` to handle `localhost` connections.
2.  **Phase 10.3 (Verify)**:
    *   Verify Project Creation (should be instant, no permission errors).
    *   Verify GPU usage (native access or via local Ollama).

## 5. Conclusion

The "Failed to create project" error was a symptom. The disease is the architecture. **Pivoting to a Host-Native Runtime** is the correct holistic approach to build a usable, robust Local IDE.
