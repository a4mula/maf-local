"""
Research Executor Agent - Tier 4

This module implements the ResearchExecutor, responsible for conducting research
and answering questions based on available knowledge.
"""

from src.agents.executors.base_executor import BaseExecutor
from src.models.data_contracts import ExecutorReport
from agent_framework import AgentThread
from typing import Dict, Any

class ResearchExecutor(BaseExecutor):
    """Executor for research tasks (Tier 4).
    
    Responsibilities:
    - Execute research queries
    - Cache results for performance
    - Return structured findings
    """
    
    def __init__(self, chat_client, tools: list = None):
        """Initialize ResearchExecutor.
        
        Args:
            chat_client: MAF chat client
            tools: List of tools (e.g., search tools)
        """
        super().__init__(
            chat_client=chat_client,
            executor_type="Research",
            tools=tools
        )
        self._cache: Dict[str, str] = {}
        
    async def execute_task(
        self, 
        task: dict, 
        thread: AgentThread
    ) -> ExecutorReport:
        """Execute research task with caching.
        
        Args:
            task: Task dictionary
            thread: AgentThread
            
        Returns:
            ExecutorReport
        """
        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")
        
        # Check cache
        if description in self._cache:
            return ExecutorReport(
                executor_task_id=task_id,
                executor_name=self.name,
                status="Completed",
                outputs={"artifact": self._cache[description]},
                metadata={"executor_type": self.executor_type, "cached": True}
            )
            
        # Execute via base class
        report = await super().execute_task(task, thread)
        
        # Cache successful results
        if report.status == "Completed" and "artifact" in report.outputs:
            self._cache[description] = report.outputs["artifact"]
            
        return report

    def clear_cache(self):
        """Clear the research cache."""
        self._cache.clear()
