# MAF Local (Hierarchical DevStudio)

**A GPU-accelerated, local-first development environment for the Microsoft Agent Framework (MAF SDK).**

This repository provides a complete, containerized studio for building, testing, and observing hierarchical multi-agent systems. It is designed to run locally on NVIDIA hardware, leveraging **Ollama** for local inference and **LiteLLM** for unified model access.

---

- **Containerized Workflow**: One-command startup via Docker Compose.
- **Host-Native Agents**: Agents run natively for performance and file access.
- **4-Tier Hierarchy**: Strict separation of Strategy, Tactics, and Execution.

---

## 🛠️ Prerequisites

- **Linux OS** (Tested on Ubuntu/Debian)
- **NVIDIA GPU** (8GB+ VRAM recommended for Llama 3.1 8B)
- **NVIDIA Container Toolkit** (Required for GPU passthrough to Docker)
- **Docker & Docker Compose** (v2.0+)
- **Python 3.10+** (For local CLI tools)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/maf-local.git
cd maf-local
```

### 2. Configure Environment
The system will automatically generate a default `.env` file on first run, but you can create one manually to set your API keys.

```bash
# Create .env file
echo "LITELLM_MASTER_KEY=sk-maf-secure-2025-key" > .env
# Optional: Add Gemini API Key for cloud fallback
echo "GEMINI_API_KEY=your_key_here" >> .env
```


### 3. Start Infrastructure Services
First, start the Docker infrastructure services (database, AI models, etc.):

```bash
docker compose up -d
```

This starts:
- PostgreSQL (database)
- Ollama (local LLM)
- ChromaDB (vector store)
- LiteLLM (unified AI gateway)
- Prometheus + Grafana (observability)

### 4. Start the MAF Studio Application
Run the Host-Native startup script:

```bash
./run_studio.sh
```

This script will:
1. Create/activate Python virtual environment (`.venv`)
2. Install dependencies from `requirements.txt`
3. Set environment variables for localhost services
4. Start Agent API (background)
5. Start Streamlit UI (foreground)

**Note:** The Agent and UI run natively on your host, not in containers, for better performance and native file access.

---

## 🖥️ Usage

Once the node is running, you can access the following interfaces:

### 1. MAF Studio UI
**URL:** [http://localhost:8501](http://localhost:8501)
- **Chat Interface**: Interact with the Liaison Agent to plan projects or ask questions.
- **Live Graph**: View the real-time hierarchy and status of all active agents.

### 2. Observability Dashboards
- **Grafana:** [http://localhost:3000](http://localhost:3000) (Default login: `admin` / `admin`)
- **Prometheus:** [http://localhost:9093](http://localhost:9093)

---

## 📂 Project Structure

The project is organized as follows:

```text
maf-local/
├── config/                 # Configuration files (LiteLLM, Prometheus)
├── docker/                 # Dockerfiles for all services
├── docs/                   # Documentation (Planning, Vision, Feedback)
├── scripts/                # Utility scripts (Startup, Migrations)
├── src/                    # Source code for Agents and API
│   ├── agents/
│   │   ├── executors/      # Tier 4: Coder, Tester, Writer
│   │   ├── domain_leads/   # Tier 3: Dev, QA, Docs
│   │   └── ...
│   ├── workflows/          # OLB and TLB Workflows
│   ├── tools/              # MAF @ai_function tools
│   └── ...
├── tests/                  # Unit and Verification tests
├── ui-next/                # Next.js source for Live Graph
└── docker-compose.yaml     # Service orchestration
```

---

## 🏗️ Architecture (Phase 2 Status)

The system implements a **4-Tier Unified Batching Engine (UBE)** architecture:

```
Tier 1: Interface
   [LiaisonAgent]
        ↓
Tier 2: Orchestration (Strategy)
   [ProjectLeadAgent] ↔ [DocumentationAgent] (Peers)
        ↓ (OLB Workflow)
Tier 3: Tactical (Domain Leads)
   [DevDomainLead] [QADomainLead] [DocsDomainLead]
        ↓ (TLB Workflow)
Tier 4: Execution (Atomic)
   [CoderExecutor] [TesterExecutor] [WriterExecutor]
```

### Key Components:
- **OLB (Orchestration Level Batcher):** Routes strategic plans to Domain Leads.
- **TLB (Tactical Level Batcher):** Orchestrates parallel execution of atomic tasks.
- **PermissionFilter:** Enforces Principle of Least Authority (PoLA) for file operations.
- **Pure MAF Tools:** All tools use standard `@ai_function` decorators with Pydantic models.

---

## 📚 Documentation

This project uses an **agent-optimized documentation system** designed for both human developers and AI agents.

### For Humans 👥

**Start here:** [`docs/README.md`](./docs/README.md) - Complete documentation navigation guide

**Quick Links:**
- 🚀 [Quick Start Guide](./docs/03_GUIDES/QUICKSTART.md) - Get up and running in 10 minutes
- 🏗️ [Current Architecture](./docs/01_ARCHITECTURE/CURRENT.md) - System design and components
- 📋 [Current Tasks](./docs/02_PLANNING/TASKS.md) - Active work
- ❓ [Why Hierarchical Agents?](./docs/00_META/PHILOSOPHY.md) - Design rationale
- 🔮 [Vision](./docs/02_PLANNING/ROADMAP.md) - Long-term roadmap

### For Agents 🤖

**Agent Workspace:** [`docs/00_META/.ai/`](./docs/00_META/.ai/)

**Required Reading (in order):**
1. [`GUIDELINES.md`](./docs/00_META/.ai/GUIDELINES.md) - Coding standards and MAF SDK compliance rules
2. [`MANIFEST.yaml`](./docs/00_META/.ai/MANIFEST.yaml) - Feature tracking and navigation shortcuts
3. [`agents.md`](./docs/00_META/.ai/agents.md) - Agent roles, tools, and boundaries

**Navigation Shortcuts:**
- What am I working on? → [`02_PLANNING/TASKS.md`](./docs/02_PLANNING/TASKS.md)
- What is the system? → [`01_ARCHITECTURE/CURRENT.md`](./docs/01_ARCHITECTURE/CURRENT.md)
- Why does X exist? → [`00_META/PHILOSOPHY.md`](./docs/00_META/PHILOSOPHY.md)

---

## 🛑 Stopping the Node

To stop all services:

```bash
docker compose down
```
