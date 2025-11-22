---
type: tutorial
audience: beginner
status: published
last_updated: 2025-11-21
related:
  - ../how-to/deploy_with_docker.md
  - ../architecture/CURRENT_STATE.md
tags: [quickstart, setup, docker, ollama]
feature_refs: []
---

# Quickstart: Getting Started with MAF Local

This tutorial will guide you through setting up and running the Hierarchical MAF Studio on your local machine for the first time.

**What you'll learn:**
- How to start the entire MAF Local stack
- How to access the web interfaces
- How to send your first message to the agents
- What to expect from the system

**Estimated time:** 10 minutes

---

## Prerequisites

Before you begin, ensure you have:
- **NVIDIA GPU** with CUDA drivers installed (RTX 3060 Ti or better recommended)
- **Docker** and **Docker Compose** (v2.0+) installed
- **8GB+ VRAM** available
- **Python 3.10+** (for local development scripts)

To verify GPU access:
```bash
nvidia-smi
```

You should see your GPU listed.

---

## Step 1: Clone the Repository

```bash
cd ~projects/
git clone https://github.com/a4mula/maf-local.git
cd maf-local
```

---

## Step 2: Create Environment File

Create a `.env` file in the project root with your API keys:

```bash
# Copy the example
cp .env.example .env

# Edit with your keys
nano .env
```

**Required variables:**
```bash
LITELLM_MASTER_KEY=sk-maf-secure-2025-key  # Can be any string
GEMINI_API_KEY=your_gemini_api_key_here     # Get from https://aistudio.google.com/apikey
```

> [!TIP]
> The `LITELLM_MASTER_KEY` can be any string—it's used for internal authentication.
> Gemini is optional but recommended for fallback when local models struggle.

---

## Step 3: Start Infrastructure Services

First, start the Docker infrastructure services:

```bash
docker compose up -d
```

This starts the backend services:
- PostgreSQL (database)
- Ollama (local LLM - pulls Llama 3.1 8B model ~4.7GB on first run)
- ChromaDB (vector store)
- LiteLLM (unified AI gateway)
- Prometheus + Grafana (observability)

**First run:** Takes 5-10 minutes (model download)  
**Subsequent runs:** ~30 seconds

Wait for services to be ready:
```bash
# Watch until all services show "healthy" or "running"
docker compose ps
```

---

## Step 4: Start the MAF Studio Application

Run the Host-Native startup script:

```bash
./run_studio.sh
```

This script will:
1. Create/activate Python virtual environment (`.venv`)
2. Install dependencies from `requirements.txt`
3. Set environment variables for localhost services
4. Start Agent API (background on port 8002)
5. Start Streamlit UI (foreground on port 8501)

> [!NOTE]
> **Host-Native Architecture:** The Agent and UI run natively on your host (not in containers) for better performance and direct file access.

---

## Step 5: Verify Services

Check that Docker infrastructure is running:

```bash
docker ps
```

You should see these containers:
- `maf-ollama` (port 11434)
- `maf-litellm` (port 4000)
- `maf-postgres` (port 5432)
- `maf-chroma` (port 8000)
- `prometheus` (port 9093)
- `grafana` (port 3000)

---

## Step 5: Access the Web Interfaces

Open your browser to these URLs:

### Streamlit Chat Interface
**URL:** http://localhost:8501

This is where you'll interact with the Liaison Agent.

### Live Agent Graph
**URL:** http://localhost:3000

Real-time visualization of the agent hierarchy and status.

### Grafana Dashboard
**URL:** http://localhost:3001  
**Login:** `admin` / `admin` (change on first login)

Metrics and observability.

---

## Step 6: Send Your First Message

In the Streamlit interface:

1. **Type a question:**
   ```
   What is the current architecture of this system?
   ```

2. **Watch the agent graph** (http://localhost:3000) to see:
   - Liaison Agent receives your message
   - Liaison classifies it as a "Question"
   - Liaison forwards to Project Lead
   - Project Lead retrieves context from files
   - Project Lead formulates a detailed response

3. **Review the response** in Streamlit

---

## Step 7: Try an Idea

Now send an **idea** instead of a question:

```
I want to add a new REST API endpoint that returns the current system status.
```

**What happens:**
- Liaison classifies as "Idea"  
- Liaison forwards to Project Lead
- Project Lead analyzes the request
- Project Lead stores a decision in the governance database
- **Project Lead responds with analysis** (text response)

> [!IMPORTANT]
> **Current Limitation:** Agents currently function as "intelligent chatbots" that analyze and respond to ideas, but do **not yet** autonomously implement workflows or generate code files.
>
> See [`docs/planning/CURRENT.md`](../planning/CURRENT.md) for the re-alignment plan to enable full autonomous development.

---

## Verification

You've successfully completed the quickstart if:
- ✅ All 9 Docker containers are running
- ✅ Streamlit responds to your messages
- ✅ Agent graph shows real-time updates
- ✅ Grafana displays system metrics

---

## Troubleshooting

**Problem:** Ollama fails to start

**Solution:**
```bash
# Check GPU access
nvidia-smi

# Restart Ollama container
docker restart maf-ollama
```

---

**Problem:** Streamlit shows "Connection refused"

**Solution:**
```bash
# Check agent container logs
docker logs maf-agent

# Restart the agent
docker restart maf-agent
```

---

**Problem:** Agents don't respond

**Solution:**
```bash
# Check LiteLLM is running
curl http://localhost:4000/health

# Verify API key is set
docker exec maf-litellm env | grep GEMINI_API_KEY
```

---

## Next Steps

Now that you're up and running:

1. **Explore the Architecture**: Read [Current Architecture](../architecture/CURRENT.md)
2. **Learn the Deployment**: See [Deployment Guide](./DEPLOYMENT.md)
3. **Understand the Vision**: Read [Future Vision](../vision/FUTURE.md)
4. **Review Current Work**: See [Planning](../planning/CURRENT.md)
5. **Dive into Code**: Browse `src/agents/` to see agent implementations

---

## Stopping the System

When you're done:

```bash
docker compose down
```

To remove all data (database, volumes):
```bash
docker compose down -v
```

---

## Summary

You've learned how to:
- ✅ Set up the environment with `.env`
- ✅ Start all services with one command
- ✅ Access the web interfaces
- ✅ Interact with the agent system
- ✅ Verify everything is working

**Estimated completion time:** 10 minutes ⏱️

Welcome to MAF Local! 🎉
