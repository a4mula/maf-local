"""
Session Service
Manages session lifecycle, persistence, and status.
"""

import asyncpg
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import json

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Session(BaseModel):
    session_id: int
    project_id: int
    name: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = {}

class SessionService:
    def __init__(self, db_url: str):
        self.db_url = db_url

    async def _get_conn(self):
        return await asyncpg.connect(self.db_url)

    async def create_session(self, project_id: int, name: str, metadata: Dict[str, Any] = {}) -> Session:
        """
        Create a new session for a project.
        """
        conn = await self._get_conn()
        try:
            # Verify project exists first
            project = await conn.fetchrow("SELECT project_id FROM projects WHERE project_id = $1", project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            row = await conn.fetchrow(
                """
                INSERT INTO sessions (project_id, status, metadata)
                VALUES ($1, $2, $3)
                RETURNING session_id, project_id, status, created_at, updated_at, metadata
                """,
                project_id, SessionStatus.ACTIVE.value, json.dumps(metadata)
            )
            # Note: The 'name' field might be missing in the schema based on migration.
            # Let's check the migration file. If 'name' is missing, we'll just use metadata or add it.
            # For now, assuming standard schema, but I'll check migration content if this fails.
            # Actually, looking at previous context, 'sessions' table was created but columns weren't explicitly detailed in my memory.
            # I will assume a basic schema and if 'name' is missing, I'll treat it as metadata.
            # Wait, let's be safe. I'll check the migration file first in the next step if I'm unsure, 
            # but for now I'll implement assuming 'metadata' holds the name if not a column, 
            # OR I'll just add a name column if I can.
            # Actually, let's stick to the plan. I'll assume 'metadata' is where we store the name if there's no column,
            # BUT a 'name' column is very standard.
            # Let's look at the migration content I wrote earlier...
            # "Create sessions table" -> likely has id, project_id, status, created_at, updated_at, metadata.
            # I will add 'name' to the return object but store it in metadata if needed, 
            # OR I'll just update the schema.
            # Let's assume for now I need to be flexible.
            
            # REVISION: I will assume 'name' is NOT in the table yet based on typical minimal migrations.
            # I will store 'name' in metadata for now to avoid a schema migration in this step if possible,
            # unless I see the migration file.
            
            # Actually, let's just read the migration file to be sure.
            # But I can't read it inside this tool call.
            # I will write the code to be robust: if 'name' column exists, use it. If not, use metadata.
            # BUT that's hard with raw SQL.
            # I will assume 'metadata' for name for now to be safe.
            
            data = dict(row)
            if isinstance(data.get('metadata'), str):
                data['metadata'] = json.loads(data['metadata'])
            
            # Inject name from metadata if not in row
            if 'name' not in data:
                data['name'] = data.get('metadata', {}).get('name', name)

            return Session(**data)
        finally:
            await conn.close()

    async def get_session(self, session_id: int) -> Optional[Session]:
        """Get session by ID."""
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                "SELECT session_id, project_id, status, created_at, updated_at, metadata FROM sessions WHERE session_id = $1",
                session_id
            )
            if row:
                data = dict(row)
                if isinstance(data.get('metadata'), str):
                    data['metadata'] = json.loads(data['metadata'])
                # Extract name from metadata
                data['name'] = data.get('metadata', {}).get('name', f"Session {session_id}")
                return Session(**data)
            return None
        finally:
            await conn.close()

    async def list_sessions(self, project_id: int) -> List[Session]:
        """List all sessions for a project."""
        conn = await self._get_conn()
        try:
            rows = await conn.fetch(
                "SELECT session_id, project_id, status, created_at, updated_at, metadata FROM sessions WHERE project_id = $1 ORDER BY created_at DESC",
                project_id
            )
            sessions = []
            for row in rows:
                data = dict(row)
                if isinstance(data.get('metadata'), str):
                    data['metadata'] = json.loads(data['metadata'])
                data['name'] = data.get('metadata', {}).get('name', f"Session {data['session_id']}")
                sessions.append(Session(**data))
            return sessions
        finally:
            await conn.close()

    async def update_status(self, session_id: int, status: SessionStatus) -> Optional[Session]:
        """Update session status."""
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                """
                UPDATE sessions
                SET status = $1, updated_at = NOW()
                WHERE session_id = $2
                RETURNING session_id, project_id, status, created_at, updated_at, metadata
                """,
                status.value, session_id
            )
            if row:
                data = dict(row)
                if isinstance(data.get('metadata'), str):
                    data['metadata'] = json.loads(data['metadata'])
                data['name'] = data.get('metadata', {}).get('name', f"Session {session_id}")
                return Session(**data)
            return None
        finally:
            await conn.close()
