"""
Base Domain Lead Agent

Tier 3 agent responsible for tactical planning and executor orchestration.
Bridges the gap between Project Lead (Strategy) and Executors (Execution).
"""

from agent_framework import ChatAgent, AgentThread
from src.models.data_contracts import TaskDefinition, ExecutorReport
from src.workflows.tlb_workflow import TLBWorkflow
from src.utils import get_logger
from typing import List, Dict, Any, Optional
import json

logger = get_logger(__name__)


class BaseDomainLead(ChatAgent):
    """Base class for Domain Lead agents (Tier 3: Tactical Layer).
    
    Domain Leads are responsible for:
    1. Receiving high-level TaskDefinitions from Project Lead (via OLB)
    2. Breaking down tasks into atomic subtasks for Executors
    3. Orchestrating execution via TLBWorkflow
    4. Validating results and reporting back to Project Lead
    
    Attributes:
        domain (str): The domain this agent manages (e.g., "Frontend", "Backend")
        tlb_workflow (TLBWorkflow): Workflow for executor orchestration
    """
    
    def __init__(
        self, 
        chat_client, 
        domain: str, 
        tlb_workflow: TLBWorkflow,
        instructions: str
    ):
        """Initialize Domain Lead agent.
        
        Args:
            chat_client: MAF chat client
            domain: Domain name (e.g., "Frontend")
            tlb_workflow: TLBWorkflow instance for executor orchestration
            instructions: Specific instructions for this domain
        """
        base_instructions = f"""You are the {domain} Domain Lead (Tier 3).
        
Your Goal: Convert high-level tasks into working software artifacts.

Responsibilities:
1. ANALYZE the assigned TaskDefinition
2. BREAK DOWN the task into atomic subtasks for Executors (Coder, Tester, Writer)
3. ORCHESTRATE execution using the TLB Workflow
4. VALIDATE the results (did the executors succeed?)
5. REPORT back to the Project Lead

Available Executors:
- CoderExecutor: Writes code artifacts
- TesterExecutor: Writes test artifacts
- WriterExecutor: Writes documentation artifacts

You do NOT write code yourself. You delegate to Executors.
"""
        super().__init__(
            name=f"{domain}DomainLead",
            instructions=f"{base_instructions}\n\n{instructions}",
            tools=[],  # DLs don't use tools directly, they use the TLB workflow
            chat_client=chat_client
        )
        self.domain = domain
        self.tlb_workflow = tlb_workflow
        
    async def execute_task(
        self, 
        task_def: TaskDefinition, 
        thread: AgentThread
    ) -> Dict[str, Any]:
        """Execute a high-level task by delegating to executors.
        
        Args:
            task_def: The high-level task from Project Lead
            thread: MAF AgentThread
            
        Returns:
            Summary of execution results
        """
        logger.info(f"[{self.name}] Received task: {task_def.description}")
        
        # 1. Break down task into subtasks
        subtasks = await self._break_down_task(task_def, thread)
        logger.info(f"[{self.name}] Generated {len(subtasks)} subtasks")
        
        # 2. Execute subtasks via TLB
        tlb_result = await self.tlb_workflow.execute_tasks(subtasks, thread)
        
        # 3. Analyze results
        success = tlb_result["failed"] == 0
        
        return {
            "task_id": task_def.task_id,
            "status": "Completed" if success else "Failed",
            "tlb_result": tlb_result,
            "summary": f"Executed {tlb_result['total_tasks']} subtasks. Success: {success}"
        }
        
    async def _break_down_task(
        self, 
        task_def: TaskDefinition, 
        thread: AgentThread,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """Use LLM to break down high-level task into executor subtasks.
        
        Args:
            task_def: The high-level task
            thread: MAF AgentThread
            max_retries: Number of retries for JSON parsing failures
            
        Returns:
            List of subtask dictionaries for TLB
        """
        prompt = f"""
        BREAK DOWN this high-level task into atomic subtasks for Executors.
        
        Task: {task_def.description}
        Domain: {self.domain}
        
        Available Executors:
        - "coder": Writes code
        - "tester": Writes tests
        - "writer": Writes docs
        
        Return a JSON list of objects with:
        - description: Specific instruction for the executor
        - executor_type: "coder", "tester", or "writer"
        - task_id: A unique subtask ID (e.g., "{task_def.task_id}_sub1")
        
        Example JSON format:
        [
            {{"description": "Write a function to...", "executor_type": "coder", "task_id": "t1_sub1"}},
            {{"description": "Write a test for...", "executor_type": "tester", "task_id": "t1_sub2"}}
        ]
        
        RETURN ONLY JSON. NO MARKDOWN.
        """
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await self.run(prompt, thread=thread)
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                # Clean up response (remove markdown code blocks if present)
                cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
                
                subtasks = json.loads(cleaned_text)
                # Validate structure
                for task in subtasks:
                    if "description" not in task or "executor_type" not in task:
                        raise ValueError("Invalid subtask structure")
                return subtasks
                
            except Exception as e:
                logger.warning(f"[{self.name}] Attempt {attempt + 1}/{max_retries} failed: {e}")
                last_error = e
                # Add error context to prompt for next retry
                prompt += f"\n\nPREVIOUS ATTEMPT FAILED: {str(e)}. PLEASE FIX JSON FORMAT."

        logger.error(f"[{self.name}] All {max_retries} attempts failed. Error: {last_error}")
        # Fallback: Create one generic subtask
        return [{
            "description": f"Implement: {task_def.description}",
            "executor_type": "coder",
            "task_id": f"{task_def.task_id}_fallback"
        }]
