# maf-local

## Overview
`maf-local` is a reproducible, containerized baseline for agent orchestration experiments.
Phase 0 establishes hygiene, infrastructure, and core components with intentional commits, ensuring a clean foundation for future development.

## Project Structure
- **.gitignore** — excludes caches, secrets, and transient files
- **Dockerfile.litellm** / **docker-compose.yaml** — containerization and orchestration baseline
- **litellm_config.yaml** / **requirements.txt** — runtime configuration and dependencies
- **src/main.py** — entrypoint for orchestrator execution
- **src/agents/** — core agent logic
- **src/services/** — agent factory and supporting services
- **src/clients/** — base client and LiteLLM integration
- **src/middleware/** — audit and permission filters
- **src/persistence/** — audit log and message store
- **src/tools/** — code tools and database provider
- **src/workflows/** — main orchestrator workflow

## Getting Started
1. Clone the repo:
   ```bash
   git clone git@github.com:a4mula/maf-local.git
   cd maf-local
2. Build and run with Docker:
   '''bash
   docker-compose up --build
3. Run locally:
   '''bash
   python src/main.py
   
## Phase 0 Baseline

This repository has been rebuilt from scratch with intentional commits:

    Hygiene enforced via .gitignore

    Infrastructure and configuration locked in

    Core agent, client, middleware, persistence, tools, and workflows established

    Tagged as phase-0 for reproducibility

## Next Steps

    Expand orchestration workflows

    Add CI/CD pipelines

    Document agent behaviors and integration patterns
