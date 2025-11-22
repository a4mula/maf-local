"""
Project Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os

from src.services.project_service import ProjectService, Project

router = APIRouter(prefix="/projects", tags=["projects"])

# Dependency to get ProjectService
# In a real app, this might come from a dependency injection container
def get_project_service():
    db_url = os.getenv("DATABASE_URL", "postgresql://maf_user:maf_pass@maf-postgres:5432/maf_db")
    return ProjectService(db_url)

class RegisterProjectRequest(BaseModel):
    path: str
    name: str

@router.get("/", response_model=List[Project])
async def list_projects(service: ProjectService = Depends(get_project_service)):
    """List all registered projects."""
    return await service.list_projects()

@router.post("/", response_model=Project)
async def register_project(
    request: RegisterProjectRequest,
    service: ProjectService = Depends(get_project_service)
):
    """Register a new project from a local path."""
    try:
        return await service.register_project(request.path, request.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    """Get project details by ID."""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
