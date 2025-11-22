"""
Project Service
Manages project registration, metadata, and validation.
"""

import os
import asyncpg
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Project(BaseModel):
    project_id: int
    name: str
    path: str
    created_at: Optional[Any] = None

class ProjectService:
    def __init__(self, db_url: str):
        self.db_url = db_url

    async def _get_conn(self):
        return await asyncpg.connect(self.db_url)

    async def register_project(self, path: str, name: str) -> Project:
        """
        Register a new project from a local path.
        """
        # 1. Ensure directory exists
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Failed to create project directory: {e}")
        
        if not os.path.isdir(path):
            raise ValueError(f"Path exists but is not a directory: {path}")
        
        # Normalize path
        abs_path = os.path.abspath(path)

        conn = await self._get_conn()
        try:
            # 2. Insert into DB
            row = await conn.fetchrow(
                """
                INSERT INTO projects (name, path)
                VALUES ($1, $2)
                RETURNING project_id, name, path, created_at
                """,
                name, abs_path
            )
            return Project(**dict(row))
        finally:
            await conn.close()

    async def list_projects(self) -> List[Project]:
        """List all registered projects."""
        conn = await self._get_conn()
        try:
            rows = await conn.fetch("SELECT project_id, name, path, created_at FROM projects ORDER BY project_id ASC")
            return [Project(**dict(row)) for row in rows]
        finally:
            await conn.close()

    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                "SELECT project_id, name, path, created_at FROM projects WHERE project_id = $1",
                project_id
            )
            if row:
                return Project(**dict(row))
            return None
        finally:
            await conn.close()

    async def get_project_by_path(self, path: str) -> Optional[Project]:
        """Get project by path."""
        abs_path = os.path.abspath(path)
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                "SELECT project_id, name, path, created_at FROM projects WHERE path = $1",
                abs_path
            )
            if row:
                return Project(**dict(row))
            return None
        finally:
            await conn.close()
