---
type: how-to
audience: practitioner  
status: published
last_updated: 2025-11-22
related:
  - ./QUICKSTART.md
tags: [docker, deployment, host-native]
feature_refs: []
---

# How to Deploy MAF Local

Learn how to deploy the MAF Local stack using the Host-Native architecture.

---

## Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with CUDA drivers
- Python 3.10+ installed on host
- `.env` file configured (see [Quickstart](./QUICKSTART.md#step-2-create-environment-file))

---

## Deployment Architecture

**Host-Native Model:**
- **Infrastructure Services** (Docker): PostgreSQL, Ollama, ChromaDB, LiteLLM, Prometheus, Grafana
- **Application Services** (Host): Agent API, Streamlit UI

This provides:
- ✅ Better performance (no container overhead for app)
- ✅ Native file access (no permission issues)
- ✅ Easier debugging (direct Python execution)

---

## Steps

### 1. Navigate to project directory

```bash
cd /home/robb/projects/maf-local
```

### 2. Start Infrastructure Services

Start the Docker backend services:

```bash
docker compose up -d
```

This starts:
- `maf-postgres` (port 5432)
- `maf-ollama` (port 11434) - Downloads Llama 3.1 8B on first run (~4.7GB)
- `maf-chroma` (port 8000)
- `maf-litellm` (port 4000)
- `prometheus` (port 9093)
- `grafana` (port 3000)

**Expected startup sequence:**
1. PostgreSQL starts first (database)
2. ChromaDB starts (vector store)
3. Prometheus starts (metrics)
4. Ollama downloads model (~4.7GB on first run)
5. LiteLLM starts (model proxy)
6. Grafana starts (dashboards)

### 3. Verify Infrastructure

Check that all Docker services are running:

```bash
# List running containers
docker ps

# Check health status
docker compose ps
```

**All containers should show "healthy" or "running".**

Test each service:

```bash
# PostgreSQL
docker exec maf-postgres pg_isready -U maf_user

# Ollama
curl http://localhost:11434/api/tags

# LiteLLM
curl http://localhost:4000/health

# ChromaDB
curl http://localhost:8000/api/v1/heartbeat
```

### 4. Start Application Services

Run the Host-Native startup script:

```bash
./run_studio.sh
```

This script will:
1. Create Python virtual environment (`.venv`) if needed
2. Activate the virtual environment
3. Install/update dependencies from `requirements.txt`
4. Set environment variables (pointing to localhost Docker services)
5. Start Agent API in background (port 8002)
6. Start Streamlit UI in foreground (port 8501)

**Monitor the startup:**
- Agent API logs will scroll by
- Streamlit UI will open in your browser automatically
- Press Ctrl+C to stop both services

### 5. Verify Application

Test the Agent API:

```bash
# Health check
curl http://localhost:8002/health

# Expected response: {"status": "healthy"}
```

Test the Streamlit UI:
- Open http://localhost:8501 in your browser
- You should see the MAF Studio interface

---

## Troubleshooting

**Container failed to start**

```bash
# View logs
docker logs <container_name>

# Restart container
docker restart <container_name>
```

**Port already in use**

```bash
# Find process using port
sudo lsof -i :8501

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yaml (infrastructure)
# Or change port in run_studio.sh (application)
```

**Out of memory**

```bash
# Check Docker resource usage
docker stats

# Increase Docker Desktop memory allocation (Settings → Resources)
# Or stop other containers
```

**Agent API won't start**

```bash
# Check if .venv exists
ls -la .venv

# If not, run script again:
./run_studio.sh

# Check Python dependencies
source .venv/bin/activate
pip list | grep streamlit
```

**Database connection errors**

```bash
# Ensure PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec maf-postgres psql -U maf_user -d maf_db -c "SELECT 1"

# View database logs
docker logs maf-postgres
```

---

## Stopping the System

### Stop Application Only

Press `Ctrl+C` in the terminal running `run_studio.sh`

This stops:
- Streamlit UI
- Agent API

Infrastructure services continue running.

### Stop Everything

```bash
# Stop both application and infrastructure
docker compose down

# Optionally: Stop application first
# (Ctrl+C in run_studio.sh terminal)
# Then: docker compose down
```

To remove all data (database, volumes):
```bash
docker compose down -v
```

---

## Production Deployment Notes

> [!WARNING]
> This setup is designed for **local development**, not production deployment.

For production, consider:
1. **Security**: Change default credentials in `.env`
2. **Persistence**: Backup PostgreSQL volume regularly
3. **Monitoring**: Configure Grafana alerts
4. **Scaling**: Run multiple Agent API instances behind load balancer
5. **Isolation**: Use separate Docker networks for security

---

## Related

- [Quickstart Tutorial](./QUICKSTART.md)
- [Architecture Overview](../architecture/CURRENT.md)
- [Planning: Current Work](../planning/CURRENT.md)
