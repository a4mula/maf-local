"""
Project-aware context management.
Ensures all operations are scoped to a project_id.
"""

from typing import Optional
from contextlib import asynccontextmanager
import contextvars

# Use contextvars for async-safe thread-local storage
_project_id_ctx = contextvars.ContextVar("project_id", default=None)

class ProjectContextManager:
    """
    Thread-local storage for current project context.
    All persistence operations must check this.
    """
    
    def set_project(self, project_id: int):
        """Set active project for current session."""
        _project_id_ctx.set(project_id)
    
    def get_project(self) -> int:
        """Get active project ID."""
        pid = _project_id_ctx.get()
        if pid is None:
            # Default to 0 (DevStudio) if not set, but warn/log in future
            # For now, strict enforcement:
            raise RuntimeError("No active project set. Call set_project() first.")
        return pid
    
    def clear_project(self):
        """Clear project context."""
        _project_id_ctx.set(None)
    
    @asynccontextmanager
    async def project_scope(self, project_id: int):
        """Context manager for temporary project scope."""
        token = _project_id_ctx.set(project_id)
        try:
            yield
        finally:
            _project_id_ctx.reset(token)


# Global instance
project_context = ProjectContextManager()
