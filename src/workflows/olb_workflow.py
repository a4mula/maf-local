"""
OLB (Orchestration Level Batcher) Workflow

Responsible for routing StrategicPlan objects from Project Lead to Domain Leads.
Uses MAF routing patterns to dispatch tasks to the correct domain.

Design:
- Receives StrategicPlan from Project Lead
- Iterates through tasks in the plan
- Routes each task to the appropriate Domain Lead based on 'domain' field
- Aggregates results from all Domain Leads
- Returns final execution summary to Project Lead
"""

from agent_framework import AgentThread
from src.models.data_contracts import StrategicPlan, TaskDefinition
from src.agents.domain_leads.base_domain_lead import BaseDomainLead
from src.utils import get_logger
from typing import Dict, Any, List
from datetime import datetime

logger = get_logger(__name__)


class OLBWorkflow:
    """Orchestration Level Batcher - Routes strategic plans to Domain Leads.
    
    The OLB is a pure workflow orchestrator. It manages the flow of tasks
    from the Strategic Tier (Project Lead) to the Tactical Tier (Domain Leads).
    
    Pattern:
        Project Lead → OLB.execute_plan(plan) → Route to DLs
          → DLs execute via TLB → Return results → Aggregate → PL
    
    Responsibilities:
    - Parse StrategicPlan
    - Route tasks to correct Domain Lead (Dev, QA, Docs)
    - Handle cross-domain dependencies (sequential execution for now)
    - Aggregate results into final report
    """
    
    def __init__(self, domain_leads: Dict[str, BaseDomainLead]):
        """Initialize OLB with available Domain Leads.
        
        Args:
            domain_leads: Dictionary mapping domain names to DL instances
                         e.g., {"Development": DevDL, "QA": QADL}
        """
        self.domain_leads = domain_leads
        
    async def execute_plan(
        self, 
        plan: StrategicPlan, 
        thread: AgentThread
    ) -> Dict[str, Any]:
        """Execute a strategic plan by routing tasks to Domain Leads.
        
        Args:
            plan: The StrategicPlan object from Project Lead
            thread: MAF AgentThread
            
        Returns:
            Aggregated execution summary
        """
        logger.info(f"Executing Plan: {plan.plan_id} ({len(plan.tasks)} tasks)")
        start_time = datetime.now()
        
        results = []
        failed_tasks = []
        
        # Sort tasks by dependencies (simple topological sort or just sequential for MVP)
        # For MVP, we assume the PL has ordered them correctly or we execute sequentially.
        ordered_tasks = self._order_tasks(plan.tasks)
        
        for task in ordered_tasks:
            domain = task.domain
            dl = self.domain_leads.get(domain)
            
            if not dl:
                error = f"No Domain Lead found for domain: {domain}"
                logger.error(f"No Domain Lead found for domain: {domain}")
                failed_tasks.append({
                    "task_id": task.task_id,
                    "error": error,
                    "status": "Failed"
                })
                continue
            
            # Execute task via Domain Lead
            try:
                logger.info(f"Routing task {task.task_id} to {dl.name}")
                result = await dl.execute_task(task, thread)
                results.append(result)
                
                if result["status"] != "Completed":
                    failed_tasks.append(result)
                    # Stop on failure? For now, yes, to prevent cascading errors.
                    logger.warning(f"Task {task.task_id} failed. Stopping plan execution.")
                    break
                    
            except Exception as e:
                error = f"Error executing task {task.task_id}: {str(e)}"
                logger.error(f"Error executing task {task.task_id}: {str(e)}")
                failed_tasks.append({
                    "task_id": task.task_id,
                    "error": error,
                    "status": "Failed"
                })
                break
        
        end_time = datetime.now()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return self._aggregate_results(plan, results, failed_tasks, execution_time_ms)
    
    def _order_tasks(self, tasks: List[TaskDefinition]) -> List[TaskDefinition]:
        """Order tasks based on dependencies.
        
        For MVP, we just respect the list order, assuming PL ordered them.
        Future: Implement topological sort.
        """
        return tasks
        
    def _aggregate_results(
        self,
        plan: StrategicPlan,
        results: List[Dict[str, Any]],
        failed_tasks: List[Dict[str, Any]],
        execution_time_ms: int
    ) -> Dict[str, Any]:
        """Create final report for Project Lead."""
        total = len(plan.tasks)
        completed = len([r for r in results if r["status"] == "Completed"])
        failed = len(failed_tasks)
        pending = total - completed - failed
        
        status = "Completed" if failed == 0 and pending == 0 else "Failed"
        
        return {
            "plan_id": plan.plan_id,
            "status": status,
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "results": results,
            "failed_details": failed_tasks,
            "execution_time_ms": execution_time_ms
        }
