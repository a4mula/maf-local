cat << 'EOF' > README.md
# 🤖 Modular Agent Framework (MAF) - Local Repository

This repository establishes the foundational **Phase 0 Baseline** for the Modular Agent Framework (MAF). It is configured for **local, GPU-accelerated development** and provides a stable, reproducible LLM testing environment.

---

## ⚠️ Critical Environmental Requirements

**This repository is NOT intended for general, out-of-the-box consumption.** It is highly optimized and configured for specific hardware to ensure high performance with local LLMs.

### 1. Hardware Requirements

* **GPU:** NVIDIA GPU with dedicated CUDA support (e.g., **RTX 3060 Ti or better**).
* **VRAM:** A minimum of **8GB** dedicated VRAM is required to run the default **Llama 3.1 8B Instruct** model via Ollama.
* **Driver:** The latest NVIDIA CUDA drivers must be installed on the host machine.

### 2. Software Prerequisites

* **Docker & Docker Compose (v2.0+)**: Essential for orchestrating the multi-service stack.
* **Python 3.10+**: Required for the core agent application.

---

## 🛠️ Phase 0 Baseline Components

The repository includes all infrastructure and fixes to establish a stable local environment.

### 1. Core Services (Docker Compose)

The `docker-compose.yaml` file orchestrates the necessary services:

| Service | Technology | Purpose |
| :--- | :--- | :--- |
| **`maf-ollama`** | Ollama, Llama 3.1 8B | The local LLM provider, accelerated by the host GPU. |
| **`maf-litellm`** | LiteLLM Proxy | Standardized API endpoint for the agent to access Ollama. |
| **`maf-postgres`** | PostgreSQL | Relational database for structured persistence (Audit Logs, Agent Metadata). |
| **`maf-chroma`** | Chroma DB | Vector database for Retrieval Augmented Generation (RAG). |

### 2. Agent Infrastructure (Python)

The `src/` directory contains the core framework components, including the corrected **conversational system prompt** and **Rich output features**.

---

## ⚙️ Usage Instructions

### 1. Start the Stack

Ensure Docker is running, then execute the following command from the project root:

\`\`\`bash
docker compose up --build -d
\`\`\`

> **Note:** The `-d` flag runs containers in detached mode, freeing your terminal.

### 2. Activate and Run the Local Agent

For local development, you **must activate the virtual environment** to ensure all dependencies (`httpx`, `rich`) are found:

\`\`\`bash
# Activate the virtual environment
source .venv/bin/activate

# Run the agent as a module (required for correct package imports)
python3 -m src.main
\`\`\`

### 3. Stop the Stack

To shut down all running services:

\`\`\`bash
docker compose down
\`\`\`
EOF
