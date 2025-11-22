"""
Integration tests for Session API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.api.agent_api import app
from src.api.routes.sessions import get_session_service
from src.services.session_service import Session, SessionStatus
from datetime import datetime

# Mock Service
mock_service = AsyncMock()

def override_get_session_service():
    return mock_service

app.dependency_overrides[get_session_service] = override_get_session_service
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_mock():
    mock_service.reset_mock()

def test_create_session():
    mock_service.create_session.return_value = Session(
        session_id=1, project_id=1, name="New Session", status=SessionStatus.ACTIVE,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    
    response = client.post("/sessions/", json={"project_id": 1, "name": "New Session"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == 1
    assert data["status"] == "active"
    
    mock_service.create_session.assert_called_with(1, "New Session", {'name': 'New Session'})

def test_get_session():
    mock_service.get_session.return_value = Session(
        session_id=1, project_id=1, name="Test Session", status=SessionStatus.ACTIVE,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    
    response = client.get("/sessions/1")
    
    assert response.status_code == 200
    assert response.json()["session_id"] == 1

def test_update_status():
    mock_service.update_status.return_value = Session(
        session_id=1, project_id=1, name="Test Session", status=SessionStatus.PAUSED,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    
    response = client.patch("/sessions/1/status", json={"status": "paused"})
    
    assert response.status_code == 200
    assert response.json()["status"] == "paused"
    
    mock_service.update_status.assert_called_with(1, SessionStatus.PAUSED)

def test_list_project_sessions():
    mock_service.list_sessions.return_value = [
        Session(
            session_id=1, project_id=1, name="Session 1", status=SessionStatus.ACTIVE,
            created_at=datetime.now(), updated_at=datetime.now()
        )
    ]
    
    response = client.get("/sessions/project/1")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
