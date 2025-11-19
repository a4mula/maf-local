import importlib
import inspect
import json
from typing import List, Dict, Optional, Any
import httpx

from src.clients.base import IChatClient
from src.config.settings import settings


class LiteLLMChatClient(IChatClient):
    """
    An asynchronous chat client using the LiteLLM proxy for unified access
    to all LLM models.
    
    Updated to correctly transform MAF ToolSchema (flat) into OpenAI Tool Schema (nested).
    """
    def __init__(self, model_name: str = "maf-default", agent_type: str = "Local-Dev"):
        self.base_url = settings.LITELLM_URL
        self.model_name = model_name
        self.agent_type = agent_type
        self.api_key = settings.LITELLM_MASTER_KEY

    async def chat(
        self, 
        history: List[Dict[str, str]], 
        tools: List[Dict[str, Any]] | None = None,
        tool_choice: Optional[Any] = None 
    ) -> str:
        """
        Sends the conversation history and available tools to the LiteLLM proxy.
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 1. TRANSFORM TOOLS (Critical Fix)
        # Convert MAF flat dictionary format to OpenAI/LiteLLM nested format
        api_tools = []
        if tools:
            for t in tools:
                # If already in OpenAI format (has "type" and "function"), keep it
                if "type" in t and "function" in t:
                    api_tools.append(t)
                # If in MAF ToolSchema format (has "function_name"), transform it
                elif "function_name" in t:
                    api_tools.append({
                        "type": "function",
                        "function": {
                            "name": t["function_name"],
                            "description": t.get("description", ""),
                            "parameters": t.get("parameters", {})
                        }
                    })
        
        # Ensure None if empty list
        final_tools = api_tools if api_tools else None

        # 2. Prepare Payload
        payload = {
            "model": self.model_name,
            "messages": history,
            "tools": final_tools, 
        }

        # Add tool_choice only if tools are present
        if final_tools:
            if tool_choice:
                payload["tool_choice"] = tool_choice
            else:
                payload["tool_choice"] = "auto"

        try:
            # 3. Execute Request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    json=payload, 
                    headers=headers, 
                    timeout=60.0
                )
                response.raise_for_status()
            
            response_data = response.json()
            
            if not response_data.get("choices"):
                return "Error: Received an empty response from the LLM proxy."
            
            llm_response_message = response_data['choices'][0]['message']

            # 4. Check for tool calls
            if llm_response_message.get("tool_calls"):
                tool_call = llm_response_message["tool_calls"][0]
                function_call = tool_call["function"]
                # CRITICAL FIX: Include the tool_call["id"]
                # New format: <call:tool_call_id|function_name:{"arg": "val"}>
                return f"<call:{tool_call['id']}|{function_call['name']}:{function_call['arguments']}>"

            # 5. Return text
            return llm_response_message.get("content", "I am unable to generate a response.")

        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('error', {}).get('message', str(e))
            return f"LiteLLM HTTP Error: {error_detail}"
        except Exception as e:
            return f"An unexpected error occurred in LiteLLMClient: {e}"
