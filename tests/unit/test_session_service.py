"""
Unit tests for SessionService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.session_service import SessionService, Session, SessionStatus
from datetime import datetime
import json

@pytest.fixture
def mock_db_conn():
    conn = AsyncMock()
    # Mock fetchrow return value
    conn.fetchrow.return_value = {
        "session_id": 1,
        "project_id": 1,
        "status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "metadata": json.dumps({"name": "Test Session"})
    }
    # Mock fetch return value
    conn.fetch.return_value = [
        {
            "session_id": 1,
            "project_id": 1,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": json.dumps({"name": "Test Session"})
        }
    ]
    return conn

@pytest.fixture
def session_service(mock_db_conn):
    with patch("asyncpg.connect", return_value=mock_db_conn) as mock_connect:
        service = SessionService("postgresql://user:pass@localhost/db")
        service._connect_mock = mock_connect
        yield service

@pytest.mark.asyncio
async def test_create_session_success(session_service, mock_db_conn):
    # Mock project check
    mock_db_conn.fetchrow.side_effect = [
        {"project_id": 1}, # Project exists check
        { # Insert return
            "session_id": 1,
            "project_id": 1,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": json.dumps({"name": "Test Session"})
        }
    ]
    
    session = await session_service.create_session(1, "Test Session")
    
    assert session.session_id == 1
    assert session.name == "Test Session"
    assert session.status == SessionStatus.ACTIVE
    
    # Verify DB calls
    assert mock_db_conn.fetchrow.call_count == 2
    assert "INSERT INTO sessions" in mock_db_conn.fetchrow.call_args[0][0]

@pytest.mark.asyncio
async def test_create_session_project_not_found(session_service, mock_db_conn):
    mock_db_conn.fetchrow.return_value = None # Project check fails
    
    with pytest.raises(ValueError, match="Project 1 not found"):
        await session_service.create_session(1, "Test Session")

@pytest.mark.asyncio
async def test_get_session(session_service, mock_db_conn):
    session = await session_service.get_session(1)
    
    assert session is not None
    assert session.session_id == 1
    
    mock_db_conn.fetchrow.assert_called_once()
    assert "WHERE session_id = $1" in mock_db_conn.fetchrow.call_args[0][0]

@pytest.mark.asyncio
async def test_update_status(session_service, mock_db_conn):
    session = await session_service.update_status(1, SessionStatus.PAUSED)
    
    assert session is not None
    
    mock_db_conn.fetchrow.assert_called_once()
    assert "UPDATE sessions" in mock_db_conn.fetchrow.call_args[0][0]
    assert "status = $1" in mock_db_conn.fetchrow.call_args[0][0]
