#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting MAF Studio (Host-Native Mode)...${NC}"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

# 3. Install Dependencies
echo -e "${BLUE}⬇️  Installing dependencies...${NC}"
pip install -q -r requirements.txt

# 4. Set Environment Variables (Pointing to Localhost Docker Ports)
export DATABASE_URL="postgresql://maf_user:maf_pass@localhost:5432/maf_db"
export OLLAMA_URL="http://localhost:11434"
export CHROMA_HOST="localhost"
export CHROMA_PORT="8000"
export LITELLM_URL="http://localhost:4000"
export AGENT_API_URL="http://localhost:8002"
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 5. Start Agent API (Background)
echo -e "${GREEN}🤖 Starting Agent API on port 8002...${NC}"
python -m src.api_server > agent.log 2>&1 &
AGENT_PID=$!

# 6. Start Streamlit UI (Foreground)
echo -e "${GREEN}🖥️  Starting MAF Studio UI...${NC}"
streamlit run src/ui/streamlit_app.py

# Cleanup on exit
kill $AGENT_PID
