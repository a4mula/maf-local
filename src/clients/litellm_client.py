import importlib
import inspect
import json
from typing import List, Dict, Optional, Any
import httpx

from src.clients.base import IChatClient
from src.config.settings import settings
from src.config.tool_registry import TOOL_REGISTRY, ToolSchema 

class LiteLLMChatClient(IChatClient):
    """
    An asynchronous chat client using the LiteLLM proxy for unified access
    to all LLM models (currently Ollama/Llama 3.1).
    
    Calls the LiteLLM proxy at http://maf-litellm:4000 which routes to Ollama.
    Handles tool calling and multi-turn tool execution.
    """
    def __init__(self, model_name: str = "maf-default", agent_type: str = "Local-Dev"):
        self.client = httpx.AsyncClient()
        self.base_url = f"{settings.LITELLM_URL}/chat/completions"
        self.model_name = model_name
        self.agent_type = agent_type
        self.api_key = settings.LITELLM_MASTER_KEY
        
        # Tooling Components
        self.tool_schemas: List[Dict[str, Any]] = []
        self.tool_functions: Dict[str, Any] = {}
        
        self._load_tools()

    def _load_tools(self):
        """
        Dynamically loads tool schemas and functions from the TOOL_REGISTRY
        based on the agent's type.
        """
        if self.agent_type in TOOL_REGISTRY:
            for tool_schema_data in TOOL_REGISTRY[self.agent_type]:
                self.tool_schemas.append({
                    "type": "function",
                    "function": {
                        "name": tool_schema_data.function_name,
                        "description": tool_schema_data.description,
                        "parameters": tool_schema_data.parameters
                    }
                })

                try:
                    module = importlib.import_module(tool_schema_data.module_path)
                    func = getattr(module, tool_schema_data.function_name)
                    self.tool_functions[tool_schema_data.function_name] = func
                except Exception as e:
                    print(f"[Tooling] WARNING: Failed to load tool {tool_schema_data.function_name}. Error: {e}")

    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single function call requested by the LLM.
        """
        func_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        
        if func_name not in self.tool_functions:
            return {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": f"Error: Tool '{func_name}' is not implemented or registered."
            }

        func = self.tool_functions[func_name]
        try:
            parsed_args = json.loads(arguments)
            
            if inspect.iscoroutinefunction(func):
                result = await func(**parsed_args)
            else:
                result = func(**parsed_args)
                
            return {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": str(result)
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": f"Tool execution failed. Function: {func_name}. Error: {e}"
            }

    async def chat(self, history: List[Dict[str, str]]) -> str:
        """
        Sends the conversation history to LiteLLM proxy, handling tool calling.
        """
        current_messages = history.copy()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        for _ in range(5):
            payload = {
                "model": self.model_name,
                "messages": current_messages,
                "tools": self.tool_schemas if self.tool_schemas else None,
                "tool_choice": "auto" if self.tool_schemas else None
            }

            try:
                response = await self.client.post(self.base_url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                response_data = response.json()
                
                llm_response_message = response_data['choices'][0]['message']

                if llm_response_message.get("tool_calls"):
                    current_messages.append(llm_response_message)

                    tool_results = []
                    for tool_call in llm_response_message["tool_calls"]:
                        result_message = await self._execute_tool_call(tool_call)
                        tool_results.append(result_message)
                        
                    current_messages.extend(tool_results)
                    continue
                
                return llm_response_message.get("content", "I am unable to generate a response.")

            except httpx.HTTPStatusError as e:
                return f"LiteLLM HTTP Error: {e.response.text}"
            except Exception as e:
                return f"An unexpected error occurred in LiteLLMClient: {e}"

        return "Max tool call recursion limit reached. Please rephrase your request."
