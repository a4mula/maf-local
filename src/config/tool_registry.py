from pydantic import BaseModel
from typing import List, Dict, Any

# --- 1. SCHEMA DEFINITION ---
class ToolSchema(BaseModel):
    """
    MAF Standard Schema for Tool Registration.
    Defines the function's name, description, and API parameters, 
    matching the format LiteLLM/OpenAI expects.
    """
    function_name: str
    description: str
    parameters: Dict[str, Any]
    module_path: str # The path to the Python file where the function is defined

# --- 2. THE CENTRAL REGISTRY ---
# Maps Canonical Agent Types to the list of tools they are permitted to call.
TOOL_REGISTRY: Dict[str, List[ToolSchema]] = {
    # The 'Local-Dev' agent we are running now
    "Local-Dev": [
        ToolSchema(
            function_name="execute_code",
            description="Executes arbitrary Python code in a restricted sandbox environment. Use this only for complex computation or validation tasks.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The complete Python code block to execute."}
                },
                "required": ["code"]
            },
            module_path='src.tools.code_tools'
        ),
        ToolSchema(
            function_name="query_agent_messages",
            description="Queries the agent's persistence store for past conversation messages based on filters. Useful for checking memory.",
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Optional: Filter by a specific session ID."},
                    "role": {"type": "string", "description": "Optional: Filter by message role (user or assistant)."}
                }
            },
            module_path='src.tools.database_tool_provider'
        ),
    ],
    # You can extend this with other types later
    "Research-Agent": []
}
