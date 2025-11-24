"""
Base Executor Agent - Atomic Task Execution

This module provides the base class for all Executor agents in the UBE architecture.
Executors are Tier 4 agents responsible for atomic task execution with NO decision-making authority.

Design Principles:
- Task-scoped context (single file or small file set)
- Pure execution (escalate ambiguity to Domain Lead)
- Structured output (ExecutorReport objects)
- No direct file access (produce artifacts only)
"""

from agent_framework import ChatAgent, AgentThread
from src.models.data_contracts import ExecutorReport
from typing import Optional


class BaseExecutor(ChatAgent):
    """Base class for Executor agents (Tier 4: Execution Layer).
    
    Executors are specialized agents that perform atomic tasks with minimal context.
    They have NO decision-making authority and must escalate any ambiguity.
    
    Responsibilities:
    - Execute single atomic task
    - Produce artifact (code, test, doc as string)
    - Return structured ExecutorReport
    - Escalate unclear requirements
    
    Decision Authority: NONE
    - If requirements unclear → escalate to DL
    - If task too broad → escalate to DL
    - If architectural choice needed → escalate to DL
    """
    
    def __init__(self, chat_client, executor_type: str, tools: list = None):
        """Initialize Executor agent.
        
        Args:
            chat_client: MAF chat client (LiteLLM)
            executor_type: Type of executor (Coder, Tester, Writer)
            tools: List of AIFunction tools (minimal for executors)
        """
        super().__init__(
            name=f"{executor_type}Executor",
            instructions=f"""You are a {executor_type} Executor in the UBE architecture.

Your role: Execute ATOMIC tasks with NO decision-making.

ATOMIC TASK DEFINITION:
- Writing a single function or class
- Writing a single test case or test suite
- Writing a specific documentation section
- Fixing a specific bug

STRICT RULES:
1. Execute the EXACT task given - no interpretation
2. If requirements are UNCLEAR → respond with "ESCALATE: [reason]"
3. If task is TOO BROAD (e.g., "Build the app") → respond with "ESCALATE: task too complex"
4. If ARCHITECTURAL decision needed → respond with "ESCALATE: need architectural guidance"
5. Produce ARTIFACT ONLY (code/test/doc as text) - NO file writes
6. Keep output FOCUSED on the specific task

Output Format:
- Success: Provide the artifact (code, test, or documentation)
- Failure: "ESCALATE: [specific reason]"

Remember: You are a SPECIALIST. Do the work, don't plan the work.""",
            tools=tools or [],
            chat_client=chat_client
        )
        self.executor_type = executor_type
        
    async def execute_task(
        self, 
        task: dict, 
        thread: AgentThread
    ) -> ExecutorReport:
        """Execute atomic task and return structured report.
        
        Args:
            task: Task dictionary with:
                - task_id: Unique identifier
                - description: Task description
                - context: Optional context (code examples, patterns)
            thread: MAF AgentThread for state management
            
        Returns:
            ExecutorReport with status, outputs, and optional error
        """
        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")
        
        try:
            # Execute task via LLM
            result = await self.run(description, thread=thread)
            result_text = result.text if hasattr(result, 'text') else str(result)
            
            # Check for escalation
            if result_text.startswith("ESCALATE:"):
                return ExecutorReport(
                    executor_task_id=task_id,
                    executor_name=self.name,
                    status="Failed",
                    outputs={},
                    error_message=result_text,
                    metadata={"escalation": True}
                )
            
            # Success: return artifact
            return ExecutorReport(
                executor_task_id=task_id,
                executor_name=self.name,
                status="Completed",
                outputs={"artifact": result_text},
                metadata={"executor_type": self.executor_type}
            )
            
        except Exception as e:
            # Unexpected error
            return ExecutorReport(
                executor_task_id=task_id,
                executor_name=self.name,
                status="Failed",
                outputs={},
                error_message=f"Execution error: {str(e)}"
            )
