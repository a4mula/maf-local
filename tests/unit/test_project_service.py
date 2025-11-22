"""
Unit tests for ProjectService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.project_service import ProjectService, Project

@pytest.fixture
def mock_db_conn():
    conn = AsyncMock()
    # Mock fetchrow return value
    conn.fetchrow.return_value = {
        "project_id": 1,
        "name": "Test Project",
        "path": "/tmp/test-project",
        "created_at": None
    }
    # Mock fetch return value
    conn.fetch.return_value = [
        {
            "project_id": 1,
            "name": "Test Project",
            "path": "/tmp/test-project",
            "created_at": None
        }
    ]
    return conn

@pytest.fixture
def project_service(mock_db_conn):
    with patch("asyncpg.connect", return_value=mock_db_conn) as mock_connect:
        service = ProjectService("postgresql://user:pass@localhost/db")
        # Inject the mock connect so we can assert on it if needed
        service._connect_mock = mock_connect
        yield service

@pytest.mark.asyncio
async def test_register_project_success(project_service, mock_db_conn):
    with patch("os.path.exists", return_value=True), \
         patch("os.path.isdir", return_value=True), \
         patch("os.path.abspath", return_value="/tmp/test-project"):
        
        project = await project_service.register_project("/tmp/test-project", "Test Project")
        
        assert project.project_id == 1
        assert project.name == "Test Project"
        assert project.path == "/tmp/test-project"
        
        # Verify DB insert
        mock_db_conn.fetchrow.assert_called_once()
        assert "INSERT INTO projects" in mock_db_conn.fetchrow.call_args[0][0]

@pytest.mark.asyncio
async def test_register_project_invalid_path(project_service):
    with patch("os.path.exists", return_value=False):
        with pytest.raises(ValueError, match="Path does not exist"):
            await project_service.register_project("/invalid/path", "Test Project")

@pytest.mark.asyncio
async def test_list_projects(project_service, mock_db_conn):
    projects = await project_service.list_projects()
    
    assert len(projects) == 1
    assert projects[0].name == "Test Project"
    
    mock_db_conn.fetch.assert_called_once()
    assert "SELECT" in mock_db_conn.fetch.call_args[0][0]

@pytest.mark.asyncio
async def test_get_project(project_service, mock_db_conn):
    project = await project_service.get_project(1)
    
    assert project is not None
    assert project.project_id == 1
    
    mock_db_conn.fetchrow.assert_called_once()
    assert "WHERE project_id = $1" in mock_db_conn.fetchrow.call_args[0][0]
