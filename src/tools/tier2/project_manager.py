"""
Project Manager Tool
Allows agents to list, switch, and query projects.
"""

from typing import List, Dict, Any, Optional
import os
from src.services.project_service import ProjectService
from src.persistence.project_context import project_context

class ProjectManagerTool:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    async def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all available projects.
        Returns a list of project dictionaries with id, name, and path.
        """
        projects = await self.project_service.list_projects()
        return [p.dict() for p in projects]

    async def switch_project(self, project_id: int) -> str:
        """
        Switch the active project context for the current thread/session.
        Note: In the current architecture, this updates the thread-local context.
        """
        project = await self.project_service.get_project(project_id)
        if not project:
            return f"Error: Project {project_id} not found."
        
        project_context.set_project(project_id)
        return f"Switched to project: {project.name} (ID: {project_id})"

    async def get_current_project(self) -> str:
        """
        Get the currently active project.
        """
        try:
            pid = project_context.get_project()
            project = await self.project_service.get_project(pid)
            if project:
                return f"Current Project: {project.name} (ID: {pid})"
            return f"Current Project ID: {pid} (Name unknown)"
        except RuntimeError:
            return "No active project set."

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Return the JSON schema definitions for the LLM.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_projects",
                    "description": "List all available projects managed by DevStudio.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "switch_project",
                    "description": "Switch the active project context.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "The ID of the project to switch to."
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_project",
                    "description": "Get the currently active project context.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
