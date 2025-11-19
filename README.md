-----

## 📄 Finalized `README.md`

````markdown
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

### Step 1: Create Local Configuration (`.env` File)

Create a file named **`.env`** in the project root directory (`maf-local/`) and include the following variables. These are used by **Docker Compose** to configure the LiteLLM proxy and ensure proper internal authentication.

```bash
# .env file content
# --- LiteLLM Security Key ---
# This master key must be set for the LiteLLM proxy to accept tool calling requests.
# It should match the key expected by the client.
LITELLM_MASTER_KEY=sk-maf-secure-2025-key
LITELLM_URL=[http://127.0.0.1:4000](http://127.0.0.1:4000)
LITELLM_TIMEOUT=30
````

### Step 2: Start the Stack

Ensure Docker is running and the `.env` file is present, then execute the following command:

```bash
docker compose up --build -d
```

> **Note:** The `-d` flag runs containers in detached mode, freeing your terminal.

### Step 3: Activate and Run the Local Agent

For local development, you **must activate the virtual environment** to ensure all dependencies (`httpx`, `rich`) are found:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the agent as a module (required for correct package imports)
python3 -m src.main
```

### Step 4: Stop the Stack

To shut down all running services:

```bash
docker compose down
```

-----
