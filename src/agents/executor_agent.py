from agent_framework import ChatAgent
from src.tools.universal_tools import registry

class ExecutorAgent:
    """
    Tier 4: Atomic task workers
    - Single, focused task
    - Minimal context
    - Escalates ambiguity immediately
    """
    def __init__(self, role: str, chat_client):
        self.role = role  # "Coder", "Tester", "Writer"
        self.sdk_agent = ChatAgent(
            name=f"Executor_{role}",
            instructions="Execute single atomic task. Escalate any ambiguity.",
            tools=[], # Will add tools later
            chat_client=chat_client
        )

    async def execute(self, task: str):
        print(f"[Executor_{self.role}] Executing: {task}")
        # Logic to execute task
        pass
