---
type: how-to
audience: practitioner  
status: published
last_updated: 2025-11-21
related:
  - ../tutorials/01_quickstart.md
tags: [docker, deployment]
feature_refs: []
---

# How to Deploy MAF Local with Docker

Learn how to deploy the entire MAF Local stack using Docker Compose.

---

## Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with CUDA drivers
- `.env` file configured (see [Quickstart](../tutorials/01_quickstart.md#step-2-create-environment-file))

---

## Steps

### 1. Navigate to project directory

```bash
cd /path/to/maf-local
```

### 2. (Optional) Build images manually

If you want to rebuild specific containers:

```bash
# Build agent container
docker compose build maf-agent

# Build UI container
docker compose build maf-ui

# Build all
docker compose build
```

### 3. Start all services

```bash
docker compose up -d
```

The `-d` flag runs containers in detached mode (background).

### 4. Monitor startup

Watch the logs to see services starting:

```bash
# All services
docker compose logs -f

# Specific service
docker logs -f maf-agent
```

**Expected startup sequence:**
1. PostgreSQL starts first (database)
2. ChromaDB starts (vector store)
3. Prometheus starts (metrics)
4. Ollamadownloads model (~4.7GB on first run)
5. LiteLLM starts (model proxy)
6. Agent container applies migrations
7. Streamlit and Next.js UIs start

---

## Verification

Check that all services are healthy:

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

# Agent API
curl http://localhost:8002/health
```

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

# Or change port in docker-compose.yaml
```

**Out of memory**

```bash
# Check Docker resource limits
docker stats

# Increase Docker Desktop memory allocation (Settings → Resources)
# Or stop other containers
```

---

## Related

- [Quickstart Tutorial](../tutorials/01_quickstart.md)
- [Architecture Overview](../architecture/CURRENT_STATE.md)
