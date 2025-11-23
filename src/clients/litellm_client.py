import httpx
from typing import Any, MutableSequence
from collections.abc import AsyncIterable

from agent_framework import (
    BaseChatClient,
    ChatMessage,
    ChatOptions,
    ChatResponse,
    ChatResponseUpdate,
    FunctionCallContent,
    Role,
    TextContent,
    use_function_invocation,
    AIFunction
)

from src.config.settings import settings


@use_function_invocation
class LiteLLMChatClient(BaseChatClient):
    """
    MAF-compliant chat client using the LiteLLM proxy.
    
    This client extends BaseChatClient and uses the @use_function_invocation
    decorator to enable automatic tool execution through MAF's framework.
    """
    
    def __init__(self, model_name: str = "maf-default", **kwargs):
        super().__init__(**kwargs)
        self.base_url = settings.LITELLM_URL
        self.model_name = model_name
        self.api_key = settings.LITELLM_MASTER_KEY

    async def _inner_get_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Internal method to get a response from LiteLLM.
        
        This method is called by BaseChatClient.get_response() and by the
        @use_function_invocation decorator. It converts MAF objects to OpenAI
        format for LiteLLM and converts the response back to M AF format.
        """
        # 1. Convert MAF ChatMessages to OpenAI format
        history = []
        for msg in messages:
            msg_dict = {"role": str(msg.role)}
            
            # Handle different content types
            if msg.text:
                msg_dict["content"] = msg.text
            elif msg.contents:
                # Check for tool calls or function results
                tool_calls = []
                for content in msg.contents:
                    if isinstance(content, FunctionCallContent):
                        tool_calls.append({
                            "id": content.call_id,
                            "type": "function",
                            "function": {
                                "name": content.name,
                                "arguments": content.arguments
                            }
                        })
                
                if tool_calls:
                    msg_dict["tool_calls"] = tool_calls
                    msg_dict["content"] = None  # Required by OpenAI when tool_calls present
                elif any(hasattr(c, 'call_id') and hasattr(c, 'result') for c in msg.contents):
                    # This is a tool result message
                    for content in msg.contents:
                        if hasattr(content, 'call_id') and hasattr(content, 'result'):
                            msg_dict["tool_call_id"] = content.call_id
                            msg_dict["content"] = str(content.result)
                            msg_dict["role"] = "tool"
                            break
            
            history.append(msg_dict)
        
        # 2. Convert MAF tools (AIFunction or callables) to OpenAI format
        api_tools = None
        if chat_options.tools:
            from agent_framework import ai_function
            api_tools = []
            for tool in chat_options.tools:
                # Convert callables to AIFunction
                if callable(tool) and not isinstance(tool, AIFunction):
                    tool = ai_function(tool)
                
                if isinstance(tool, AIFunction):
                    # Extract schema from AIFunction
                    tool_schema = tool.to_dict()
                    api_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool_schema.get("name"),
                            "description": tool_schema.get("description", ""),
                            "parameters": tool_schema.get("input_schema", {})
                        }
                    })
        
        # 3. Prepare payload for LiteLLM
        payload = {
            "model": chat_options.model_id or self.model_name,
            "messages": history,
        }
        
        if api_tools:
            payload["tools"] = api_tools
            if chat_options.tool_choice:
                payload["tool_choice"] = str(chat_options.tool_choice)
        
        # Add other chat options
        if chat_options.temperature is not None:
            payload["temperature"] = chat_options.temperature
        if chat_options.max_tokens is not None:
            payload["max_tokens"] = chat_options.max_tokens
        
        # 4. Call LiteLLM
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('error', {}).get('message', str(e))
            raise RuntimeError(f"LiteLLM HTTP Error: {error_detail}")
        except Exception as e:
            raise RuntimeError(f"LiteLLM request failed: {e}")
        
        # 5. Convert OpenAI response back to MAF ChatResponse
        try:
            choice = data['choices'][0]
            message_data = choice['message']
            content_text = message_data.get('content')
            tool_calls = message_data.get('tool_calls')
            
            contents = []
            
            # Add text content if present
            if content_text:
                contents.append(TextContent(text=content_text))
            
            # Add tool calls if present
            if tool_calls:
                for tc in tool_calls:
                    if tc.get('type') == 'function':
                        func = tc.get('function', {})
                        contents.append(FunctionCallContent(
                            call_id=tc.get('id'),
                            name=func.get('name'),
                            arguments=func.get('arguments')
                        ))
            
            # Create ChatMessage
            chat_message = ChatMessage(
                role=Role.ASSISTANT,
                contents=contents
            )
            
            return ChatResponse(
                messages=[chat_message],
                response_id=data.get('id', 'litellm-response')
            )
            
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Error parsing LiteLLM response: {e}")

    async def _inner_get_streaming_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> AsyncIterable[ChatResponseUpdate]:
        """
        Streaming is not yet implemented for LiteLLM.
        """
        # For now, fall back to non-streaming
        response = await self._inner_get_response(
            messages=messages,
            chat_options=chat_options,
            **kwargs
        )
        # Yield the complete response as a single update
        for msg in response.messages:
            yield ChatResponseUpdate(
                role=msg.role,
                contents=msg.contents
            )
