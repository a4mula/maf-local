# Agent Graph Visualization (Next.js)

**Purpose:** Real-time visualization of the DevStudio agent hierarchy  
**Port:** 3002  
**Embedded in:** Streamlit UI via iframe

## Architecture

This Next.js application provides live graph visualization of the 4-tier UBE agent system:
- Uses React Flow for interactive node graph
- Polls `/api/agents/status` endpoint for real-time agent state
- Displays agent status, metrics, and connections

## Development

```bash
npm run dev    # Start dev server on port 3002
npm run build  # Build for production
```

## Integration

The graph is embedded in the main Streamlit UI:
```python
# In src/ui/streamlit_app.py
components.iframe("http://localhost:3002", height=410)
```

## Components

- `src/components/AgentGraph.tsx` - Main graph component with React Flow
- `src/components/AgentNode.tsx` - Custom node rendering for each agent
- `src/types/agent.ts` - TypeScript types for agent data

## API Contract

Expected response from `/api/agents/status`:
```json
{
  "nodes": [
    {"id": "liaison", "name": "Liaison", "tier": "liaison", "status": "active", ...}
  ],
  "connections": [
    {"from": "liaison", "to": "pl", "active": false}
  ],
  "activeContext": { "project_id": 0, "project_name": "..." },
  "lastUpdated": "2025-11-24T..."
}
```

## Notes

- Runs on port 3002 (3000 is Grafana)
- Auto-refreshes every 2 seconds
- Uses Tailwind CSS for styling
- TypeScript strict mode enabled
