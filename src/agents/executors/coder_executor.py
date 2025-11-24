"""
Coder Executor - Code Implementation Specialist

Atomic code generation executor with minimal context and no decision-making authority.
Produces code artifacts (strings) for Domain Lead validation, never writes files directly.
"""

from agent_framework import ChatAgent
from src.agents.executors.base_executor import BaseExecutor
from src.tools import ALL_TOOLS


class CoderExecutor(BaseExecutor):
    """Coder Executor - Code generation and implementation specialist.
    
    Context Window: Task-scoped (single file or small file set)
    Decision Authority: NONE (escalate all decisions)
    
    Capabilities:
    - Generate code artifacts from specifications
    - Refactor existing code patterns
    - Implement specific functions/classes
    - Use execute_code tool for validation
    
    Constraints:
    - NO architectural decisions
    - NO cross-file coordination
    - NO direct file access
    - Artifact output only (DL approves, FileWriter writes)
    """
    
    def __init__(self, chat_client):
        """Initialize Coder Executor.
        
        Args:
            chat_client: MAF chat client (LiteLLM)
        """
        # Coder has access to execute_code for validation
        coder_tools = [t for t in ALL_TOOLS if t.name == "execute_code"]
        
        super().__init__(
            chat_client=chat_client,
            executor_type="Coder",
            tools=coder_tools
        )
