"""
Tester Executor - Test Generation Specialist

Atomic test generation executor focused on creating test code artifacts.
"""

from src.agents.executors.base_executor import BaseExecutor
from src.tools import ALL_TOOLS


class TesterExecutor(BaseExecutor):
    """Tester Executor - Test code generation specialist.
    
    Context Window: Task-scoped (test file or test case)
    Decision Authority: NONE (escalate all decisions)
    
    Capabilities:
    - Generate unit tests
    - Generate integration tests
    - Create test fixtures
    - Use execute_code for test validation
    
    Constraints:
    - NO test strategy decisions (QA DL's responsibility)
    - NO cross-test coordination
    - Test artifact output only
    """
    
    def __init__(self, chat_client):
        """Initialize Tester Executor.
        
        Args:
            chat_client: MAF chat client (LiteLLM)
        """
        # Tester has access to execute_code for test validation
        tester_tools = [t for t in ALL_TOOLS if t.name == "execute_code"]
        
        super().__init__(
            chat_client=chat_client,
            executor_type="Tester",
            tools=tester_tools
        )
