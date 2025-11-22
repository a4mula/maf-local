"""
Session Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

from src.services.session_service import SessionService, Session, SessionStatus

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_session_service():
    db_url = os.getenv("DATABASE_URL", "postgresql://maf_user:maf_pass@maf-postgres:5432/maf_db")
    return SessionService(db_url)

class CreateSessionRequest(BaseModel):
    project_id: int
    name: str
    metadata: Optional[Dict[str, Any]] = {}

class UpdateSessionStatusRequest(BaseModel):
    status: SessionStatus

@router.post("/", response_model=Session)
async def create_session(
    request: CreateSessionRequest,
    service: SessionService = Depends(get_session_service)
):
    """Create a new session."""
    try:
        # Merge name into metadata for storage
        meta = request.metadata or {}
        meta['name'] = request.name
        return await service.create_session(request.project_id, request.name, meta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: int,
    service: SessionService = Depends(get_session_service)
):
    """Get session details."""
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.patch("/{session_id}/status", response_model=Session)
async def update_session_status(
    session_id: int,
    request: UpdateSessionStatusRequest,
    service: SessionService = Depends(get_session_service)
):
    """Update session status."""
    session = await service.update_status(session_id, request.status)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/project/{project_id}", response_model=List[Session])
async def list_project_sessions(
    project_id: int,
    service: SessionService = Depends(get_session_service)
):
    """List all sessions for a specific project."""
    return await service.list_sessions(project_id)
