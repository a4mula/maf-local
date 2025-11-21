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
                # Convert ToolMode enum to string if needed
                if hasattr(tool_choice, 'value'):
                    payload["tool_choice"] = tool_choice.value
                else:
                    payload["tool_choice"] = str(tool_choice)
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
                data = response.json()

            # 4. Return full response data for adapter to parse
            return data

        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('error', {}).get('message', str(e))
            return f"LiteLLM HTTP Error: {error_detail}"
        except Exception as e:
            return f"An unexpected error occurred in LiteLLMClient: {e}"

    async def get_response(
        self,
        messages: str | Any | list[str] | list[Any],
        *,
        tools: Optional[list] = None,
        tool_choice: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Adapter method to satisfy agent_framework.ChatClientProtocol.
        Converts MAF SDK types to LiteLLM format and back.
        """
        from agent_framework import ChatMessage, ChatResponse
        
        # Normalize messages to List[Dict[str, str]]
        history = []
        if isinstance(messages, str):
            history.append({"role": "user", "content": messages})
        elif hasattr(messages, "role") and hasattr(messages, "text"): # ChatMessage
            history.append({"role": str(messages.role), "content": messages.text})
        elif isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, str):
                    history.append({"role": "user", "content": msg})
                elif hasattr(msg, "role") and hasattr(msg, "text"): # ChatMessage
                    history.append({"role": str(msg.role), "content": msg.text})
        
        # Call existing chat method
        response_data = await self.chat(history, tools, tool_choice)
        
        if isinstance(response_data, str):
             # Error occurred
             return ChatResponse(text=f"Error: {response_data}")
             
        # Extract content from response_data
        # OpenAI format: choices[0].message.content
        try:
            choice = response_data['choices'][0]
            message = choice['message']
            content = message.get('content')
            
            # Handle tool calls if present
            # (For now, we just return text, but MAF might need tool calls in the response)
            # If content is None (tool call only), we should probably handle that.
            
            if content is None:
                content = ""
                
            return ChatResponse(text=content)
        except (KeyError, IndexError):
            return ChatResponse(text=str(response_data))
