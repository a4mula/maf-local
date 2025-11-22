"""
Integration tests for Project API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.api.agent_api import app
from src.api.routes.projects import get_project_service
from src.services.project_service import Project

# Mock Service
mock_service = AsyncMock()

def override_get_project_service():
    return mock_service

app.dependency_overrides[get_project_service] = override_get_project_service
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_mock():
    mock_service.reset_mock()

def test_list_projects():
    mock_service.list_projects.return_value = [
        Project(project_id=1, name="Test Project", path="/tmp/test")
    ]
    
    response = client.get("/projects/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Project"

def test_register_project():
    mock_service.register_project.return_value = Project(
        project_id=2, name="New Project", path="/tmp/new"
    )
    
    response = client.post("/projects/", json={"name": "New Project", "path": "/tmp/new"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == 2
    
    mock_service.register_project.assert_called_with("/tmp/new", "New Project")

def test_register_project_invalid_path():
    mock_service.register_project.side_effect = ValueError("Path does not exist")
    
    response = client.post("/projects/", json={"name": "Bad Project", "path": "/bad/path"})
    
    assert response.status_code == 400
    assert "Path does not exist" in response.json()["detail"]

def test_get_project():
    mock_service.get_project.return_value = Project(
        project_id=1, name="Test Project", path="/tmp/test"
    )
    
    response = client.get("/projects/1")
    
    assert response.status_code == 200
    assert response.json()["project_id"] == 1

def test_get_project_not_found():
    mock_service.get_project.return_value = None
    
    response = client.get("/projects/999")
    
    assert response.status_code == 404
