"""
Writer Executor - Documentation Generation Specialist

Atomic documentation generation executor focused on creating markdown doc artifacts.
"""

from src.agents.executors.base_executor import BaseExecutor


class WriterExecutor(BaseExecutor):
    """Writer Executor - Documentation generation specialist.
    
    Context Window: Task-scoped (single doc section or file)
    Decision Authority: NONE (escalate all decisions)
    
    Capabilities:
    - Generate markdown documentation
    - Create API documentation
    - Write guides and tutorials
    - Update README sections
    
    Constraints:
    - NO documentation structure decisions (Docs DL's responsibility)
    - NO cross-doc coordination
    - Documentation artifact output only
    """
    
    def __init__(self, chat_client):
        """Initialize Writer Executor.
        
        Args:
            chat_client: MAF chat client (LiteLLM)
        """
        # Writer has no tools (pure doc generation)
        super().__init__(
            chat_client=chat_client,
            executor_type="Writer",
            tools=[]
        )
