"""
Data Contracts for Unified Batching Engine (U.B.E.) Architecture.

Defines strictly-typed AFBaseSettings models for agent communication:
- TaskDefinition: Single task within a strategic plan
- StrategicPlan: Output format for ProjectLeadAgent (used by OLB for routing)
- ExecutorReport: Output format for Executor agents (used by TLB for aggregation)

These contracts enable deterministic routing and aggregation in OLB/TLB workflows.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

# Note: Using Pydantic BaseModel for now since agent_framework may not export AFBaseSettings
# If AFBaseSettings is available, import and use it instead:
# from agent_framework import AFBaseSettings

class TaskDefinition(BaseModel):
    """Defines a single task within a strategic plan.
    
    Used by ProjectLeadAgent to break down user requests into atomic tasks.
    """
    task_id: str = Field(..., description="Unique identifier for this task")
    domain: str = Field(..., description="Domain this task belongs to (e.g., 'Frontend', 'Backend', 'QA')")
    description: str = Field(..., description="Human-readable description of what this task accomplishes")
    dependencies: List[str] = Field(default_factory=list, description="List of task_ids this task depends on")
    assigned_to: Optional[str] = Field(None, description="Domain Lead agent assigned to this task (e.g., 'DevDL', 'QADL')")


class StrategicPlan(BaseModel):
    """Output format for ProjectLeadAgent.
    
    Used by OLB (Orchestration Level Batcher) to route tasks to correct Domain Leads.
    The OLB uses switch-case routing based on the 'domain' field in each TaskDefinition.
    
    Example usage in OLB:
        for task in plan.tasks:
            if task.domain == "Frontend":
                route_to(frontend_dl, task)
            elif task.domain == "Backend":
                route_to(backend_dl, task)
    """
    plan_id: str = Field(..., description="Unique identifier for this strategic plan")
    target_domains: List[str] = Field(..., description="List of domains involved in this plan (e.g., ['Frontend', 'Backend'])")
    tasks: List[TaskDefinition] = Field(..., description="Ordered list of tasks to accomplish the user's goal")
    context: Optional[str] = Field(None, description="Relevant context from DocumentationAgent (if any)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata (timestamps, priorities, etc.)")


class ExecutorReport(BaseModel):
    """Output format for Executor agents.
    
    Used by TLB (Tactical Level Batcher) to aggregate results from parallel executors.
    The TLB uses fan-in edges to collect multiple ExecutorReports and synthesize final result.
    
    Example usage in TLB:
        reports = await fan_in([coder1.run(), coder2.run(), coder3.run()])
        if all(r.status == "Completed" for r in reports):
            success = combine_outputs(reports)
    """
    executor_task_id: str = Field(..., description="ID of the task this executor was assigned")
    executor_name: str = Field(..., description="Name of the executor agent (e.g., 'CoderExecutor1')")
    status: Literal["Completed", "Failed", "Pending"] = Field(..., description="Execution status")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Task outputs (file artifacts, code snippets, test results, etc.)")
    error_message: Optional[str] = Field(None, description="Error details if status is 'Failed'")
    execution_time_ms: Optional[int] = Field(None, description="Time taken to execute this task (milliseconds)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata (logs, metrics, etc.)")


# Example usage (for documentation):
if __name__ == "__main__":
    # ProjectLeadAgent creates a StrategicPlan
    plan = StrategicPlan(
        plan_id="plan_001",
        target_domains=["Frontend", "Backend"],
        tasks=[
            TaskDefinition(
                task_id="task_001",
                domain="Frontend",
                description="Create login component in React",
                dependencies=[],
                assigned_to="DevDL"
            ),
            TaskDefinition(
                task_id="task_002",
                domain="Backend",
                description="Implement authentication API endpoint",
                dependencies=["task_001"],
                assigned_to="DevDL"
            )
        ],
        context="User wants a secure login system with JWT tokens",
        metadata={"priority": "high", "deadline": "2025-12-01"}
    )
    
    # Executor returns an ExecutorReport
    report = ExecutorReport(
        executor_task_id="task_001",
        executor_name="CoderExecutor1",
        status="Completed",
        outputs={
            "file_created": "/app/project_root/src/components/Login.tsx",
            "lines_of_code": 150,
            "tests_passed": True
        },
        execution_time_ms=5420
    )
    
    print(f"Plan: {plan.plan_id} with {len(plan.tasks)} tasks")
    print(f"Report: {report.executor_name} - {report.status}")
