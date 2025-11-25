from agent_framework import ChatAgent, ai_function, AgentThread
from src.tools import ALL_TOOLS
from src.workflows.olb_workflow import OLBWorkflow
from src.models.data_contracts import StrategicPlan, TaskDefinition
from src.utils import get_logger
from typing import List, Optional
import os
import uuid

logger = get_logger(__name__)

class ProjectLeadAgent(ChatAgent):
    """
    Tier 2: Strategic Director (MAF-Compliant)
    - Makes high-level technical decisions
    - Delegates to Domain Leads via OLB Workflow
    - Outputs STRATEGIC PLANS
    """
    def __init__(self, chat_client, olb_workflow: Optional[OLBWorkflow] = None):
        # Dynamic Project Context Loading
        context = ""
        context_paths = [
            "/app/project_root/README.md",
            "/app/project_root/.meta/project_brief.md",
            "/app/project_root/.ai/project_guidelines.md"
        ]
        
        for path in context_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context += f"\n\n# {os.path.basename(path)}\n{content}"
            except Exception as e:
                logger.warning(f"Could not load {path}: {e}")
        
        # Alternative: Try relative paths
        if not context:
            alt_paths = [
                "README.md",
                ".meta/project_brief.md",
                ".ai/project_guidelines.md"
            ]
            for path in alt_paths:
                try:
                    if os.path.exists(path):
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            context += f"\n\n# {os.path.basename(path)}\n{content}"
                except Exception as e:
                    logger.warning(f"Could not load project context: {e}")

        self.olb_workflow = olb_workflow

        # Define the strategy tool bound to this instance
        @ai_function
        async def submit_strategic_plan(
            target_domains: List[str],
            tasks: List[dict],
            plan_context: str = ""
        ) -> str:
            """
            Submit a Strategic Plan to be executed by Domain Leads.
            
            Args:
                target_domains: List of domains involved (e.g. ["Development", "QA"])
                tasks: List of task dictionaries. Each must have:
                       - description: What to do
                       - domain: "Development", "QA", or "Docs"
                       - task_id: Unique ID (optional, will be generated if missing)
                plan_context: Context/rationale for the plan
            """
            if not self.olb_workflow:
                return "Error: No OLB Workflow connected. Cannot execute plan."

            # Convert dict tasks to TaskDefinition objects
            task_defs = []
            for i, t in enumerate(tasks):
                t_id = t.get("task_id", f"task_{uuid.uuid4().hex[:8]}")
                task_defs.append(TaskDefinition(
                    task_id=t_id,
                    domain=t.get("domain", "Development"),
                    description=t.get("description", "No description"),
                    assigned_to=f"{t.get('domain', 'Dev')}DL"
                ))

            plan = StrategicPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                target_domains=target_domains,
                tasks=task_defs,
                context=plan_context
            )

            logger.info(f"Submitting plan {plan.plan_id} to OLB...")
            
            # Execute via OLB
            # We need a thread for the workflow. We can reuse the current one if passed,
            # but for a tool call, we might need to create a sub-thread or pass it.
            # For now, create a new thread for the execution context.
            exec_thread = AgentThread() 
            result = await self.olb_workflow.execute_plan(plan, exec_thread)
            
            return f"Plan Execution Result: {result['status']}\nSummary: {result}"

        # Store for testing/direct access
        self.submit_strategic_plan_tool = submit_strategic_plan

        # Combine standard tools with the instance-specific strategy tool
        agent_tools = ALL_TOOLS + [submit_strategic_plan]

        # Initialize MAF ChatAgent via inheritance
        super().__init__(
            name="ProjectLead",
            instructions=f"""You are the Project Lead. 

Your Goal: Convert user requests into executed software via Strategic Plans.

Responsibilities:
1. ANALYZE the request and Context.
2. CREATE a Strategic Plan using the `submit_strategic_plan` tool.
   - Break work into tasks for "Development", "QA", or "Docs" domains.
   - Be specific in task descriptions.
3. REVIEW the execution results returned by the tool.

Current Project Context:{context}""",
            tools=agent_tools,
            chat_client=chat_client
        )

    async def receive_idea(self, idea: str):
        """Process user idea and return strategic plan execution result."""
        logger.info(f"Received idea: {idea}")
        
        thread = AgentThread()
        response = await self.run(idea, thread=thread)
        response_text = response.text if hasattr(response, 'text') else str(response)

        logger.info(f"Finished processing: {idea[:50]}...")
        
        return f"**Project Lead Execution Report:**\n\n{response_text}"
