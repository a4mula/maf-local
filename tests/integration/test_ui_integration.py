"""
Integration tests for UI Context Flow.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.agent_api import app, active_context

client = TestClient(app)

def test_context_update_flow():
    # 1. Initial State
    response = client.get("/api/agents/status")
    assert response.status_code == 200
    data = response.json()
    assert data["activeContext"]["project_id"] == 0
    
    # 2. Update Context (Simulate Streamlit switch)
    new_context = {
        "project_id": 1,
        "project_name": "Test Project",
        "session_id": 101,
        "session_name": "Test Session"
    }
    response = client.post("/api/context", json=new_context)
    assert response.status_code == 200
    
    # 3. Verify Update
    response = client.get("/api/agents/status")
    assert response.status_code == 200
    data = response.json()
    assert data["activeContext"]["project_id"] == 1
    assert data["activeContext"]["session_name"] == "Test Session"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
