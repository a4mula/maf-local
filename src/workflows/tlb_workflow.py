"""
TLB (Tactical Level Batcher) Workflow

Responsible for executing Executor tasks in parallel and aggregating ExecutorReport objects.
Uses MAF WorkflowBuilder with fan-in/fan-out pattern for parallel execution.

Design:
- Receives task breakdown from Domain Lead
- Fans out to multiple Executors in parallel
- Uses MAF fan-in edges to aggregate results
- Returns aggregated ExecutorReport summary to Domain Lead
"""

from agent_framework import WorkflowBuilder, AgentThread
from src.models.data_contracts import ExecutorReport
from typing import List, Dict, Any
from datetime import datetime


class TLBWorkflow:
    """Tactical Level Batcher - Executes and aggregates Executor tasks.
    
    The TLB is a pure workflow orchestrator (not an agent). It manages parallel
    execution of Executor agents and aggregates their ExecutorReport outputs.
    
    Pattern:
        Domain Lead → TLB.execute_tasks(tasks) → Fan-out to Executors
          → Fan-in aggregate → Return summary to DL
    
    Responsibilities:
    - Create workflow graph with executor nodes
    - Execute tasks in parallel (fan-out)
    - Aggregate ExecutorReport objects (fan-in)
    - Return structured summary
    
    Context Window: None (stateless workflow)
    """
    
    def __init__(self, executors: Dict[str, 'BaseExecutor']):
        """Initialize TLB with available executors.
        
        Args:
            executors: Dictionary mapping executor types to executor instances
                      e.g., {"coder": CoderExecutor, "tester": TesterExecutor}
        """
        self.executors = executors
        
    async def execute_tasks(
        self, 
        tasks: List[Dict[str, Any]], 
        thread: AgentThread
    ) -> Dict[str, Any]:
        """Execute tasks in parallel and aggregate results.
        
        Args:
            tasks: List of task dictionaries, each containing:
                  - task_id: Unique identifier
                  - description: Task description
                  - executor_type: Type of executor ("coder", "tester", "writer")
                  - context: Optional context data
            thread: MAF AgentThread for state management
            
        Returns:
            Aggregated summary dictionary with:
            - total_tasks: Number of tasks executed
            - completed: Number of successful tasks
            - failed: Number of failed tasks
            - reports: List of ExecutorReport objects
            - execution_time_ms: Total execution time
        """
        if not tasks:
            return {
                "total_tasks": 0,
                "completed": 0,
                "failed": 0,
                "reports": [],
                "execution_time_ms": 0
            }
        
        start_time = datetime.now()
        
        # For MVP: Execute tasks sequentially (simpler than parallel)
        # Phase 2.1 will add true parallel execution with fan-in/fan-out
        reports = []
        
        for task in tasks:
            executor_type = task.get("executor_type", "coder")
            executor = self.executors.get(executor_type)
            
            if not executor:
                # Unknown executor type - create failed report
                reports.append(ExecutorReport(
                    executor_task_id=task.get("task_id", "unknown"),
                    executor_name=f"{executor_type}Executor",
                    status="Failed",
                    outputs={},
                    error_message=f"Unknown executor type: {executor_type}"
                ))
                continue
            
            # Execute task
            report = await executor.execute_task(task, thread)
            reports.append(report)
        
        end_time = datetime.now()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Aggregate reports
        return self._aggregate_reports(reports, execution_time_ms)
        
    def _aggregate_reports(
        self, 
        reports: List[ExecutorReport],
        execution_time_ms: int
    ) -> Dict[str, Any]:
        """Combine multiple ExecutorReports into summary.
        
        Args:
            reports: List of ExecutorReport objects
            execution_time_ms: Total execution time in milliseconds
            
        Returns:
            Aggregated summary dictionary
        """
        completed = sum(1 for r in reports if r.status == "Completed")
        failed = sum(1 for r in reports if r.status == "Failed")
        pending = sum(1 for r in reports if r.status == "Pending")
        
        return {
            "total_tasks": len(reports),
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "reports": reports,
            "execution_time_ms": execution_time_ms,
            "success_rate": completed / len(reports) if reports else 0.0
        }
