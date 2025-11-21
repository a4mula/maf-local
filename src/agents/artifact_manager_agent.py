from src.agents.core_agent_sdk import CoreAgent
from src.clients.base import IChatClient
from src.config.settings import settings

class ArtifactManagerAgent(CoreAgent):
    """
    Tier 5 Agent: Artifact Manager
    The ONLY agent authorized to touch the filesystem.
    """
    def __init__(self, chat_client: IChatClient):
        # Initialize CoreAgent with "ArtifactManager" type/role
        # This matches the role required by the execute_code tool
        super().__init__(
            client=chat_client,
            audit_log=None, # TODO: Inject audit log
            agent_type="ArtifactManager"
        )
        
        # Override system prompt to be specific
        self.sdk_agent.instructions = """
        You are the Artifact Manager. You are the ONLY agent allowed to read or write files.
        Your responsibilities:
        1. Execute code to manipulate files.
        2. Validate code before execution (basic syntax checks).
        3. Ensure no destructive operations are performed without explicit instruction.
        
        You have access to the 'execute_code' tool. Use it wisely.
        """
