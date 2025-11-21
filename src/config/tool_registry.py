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
        ToolSchema(
            function_name="search_web",
            description="Performs a web search to find current information, news, or technical documentation.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            },
            module_path='src.tools.web_search'
        ),
        ToolSchema(
            function_name="send_message",
            description="Sends a direct message to another agent. Use this to collaborate or ask for help.",
            parameters={
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "The name of the agent to send the message to."},
                    "content": {"type": "string", "description": "The message content."}
                },
                "required": ["recipient", "content"]
            },
            module_path='src.tools.communication_tools'
        ),
        ToolSchema(
            function_name="add_context",
            description="Stores a value in the persistent context for later retrieval.",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key to store the value under."},
                    "value": {"type": "string", "description": "The value to store."}
                },
                "required": ["key", "value"]
            },
            module_path='src.tools.persistent_context'
        ),
        ToolSchema(
            function_name="get_context",
            description="Retrieves a value from the persistent context.",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key to retrieve."}
                },
                "required": ["key"]
            },
            module_path='src.tools.persistent_context'
        ),
        ToolSchema(
            function_name="clear_context",
            description="Clears all stored context.",
            parameters={
                "type": "object",
                "properties": {},
            },
            module_path='src.tools.persistent_context'
        ),
    ],
    # You can extend this with other types later
    "Research-Agent": []
}
