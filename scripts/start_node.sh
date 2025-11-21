#!/bin/bash

echo "🚀 Starting Hierarchical MAF Studio Node..."

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Check for .env
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating default..."
    echo "LITELLM_MASTER_KEY=sk-1234" > .env
    echo "GEMINI_API_KEY=" >> .env
fi

# Build and Start Containers
echo "🧹 Cleaning up old containers..."
docker compose down --remove-orphans

echo "📦 Building and starting containers..."
docker compose up --build -d

echo "⏳ Waiting for services to stabilize..."
sleep 10

# Apply Migrations (using the agent container)
echo "🔄 Applying database migrations..."
# Note: apply_migrations.py is copied to /app/scripts/apply_migrations.py in the container
docker compose exec agent python3 scripts/apply_migrations.py

echo "✅ Node is running!"
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "📈 Prometheus: http://localhost:9093"
echo "🖥️  UI: http://localhost:8501"
echo ""
echo "To attach to the agent terminal:"
echo "  docker attach maf-agent"
