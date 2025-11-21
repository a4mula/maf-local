from typing import Any, MutableSequence, AsyncIterable
from agent_framework import BaseChatClient, ChatResponse, ChatMessage, ChatOptions, ChatResponseUpdate, FunctionCallContent, FunctionResultContent
from src.clients.litellm_client import LiteLLMChatClient
import json

# Import universal tools
import src.tools
from src.tools.universal_tools import registry


class LiteLLMModelClient(BaseChatClient):
    """
    Adapter that wraps LiteLLMChatClient to implement MAF SDK's BaseChatClient interface.
    
    Properly handles tool calls by converting LiteLLM/OpenAI format to MAF format.
    """
    def __init__(self, client: LiteLLMChatClient, **kwargs):
        super().__init__(**kwargs)
        self.client = client

    async def _inner_get_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Translates SDK request -> LiteLLM call -> SDK response.
        Properly handles tool calls.
        """
        # 1. Convert SDK messages to LiteLLM format
        litellm_messages = []
        for msg in messages:
            role = str(msg.role.value) if hasattr(msg.role, 'value') else str(msg.role)
            
            # Handle different message types
            if role == "tool":
                # Tool result messages - convert FunctionResultContent to tool format
                if hasattr(msg, 'contents') and msg.contents:
                    for content in msg.contents:
                        if isinstance(content, FunctionResultContent):
                            litellm_messages.append({
                                "role": "tool",
                                "tool_call_id": content.call_id,
                                "content": content.result
                            })
            elif role == "assistant" and hasattr(msg, 'contents') and msg.contents:
                # Assistant message with tool calls
                tool_calls_list = []
                text_content = msg.text if hasattr(msg, 'text') and msg.text else ""
                
                for content in msg.contents:
                    if isinstance(content, FunctionCallContent):
                        tool_calls_list.append({
                            "id": content.call_id,
                            "type": "function",
                            "function": {
                                "name": content.name,
                                "arguments": content.arguments
                            }
                        })
                
                litellm_messages.append({
                    "role": "assistant",
                    "content": text_content,
                    "tool_calls": tool_calls_list if tool_calls_list else None
                })
            else:
                # Regular text message
                litellm_messages.append({
                    "role": role,
                    "content": msg.text if hasattr(msg, 'text') else str(msg.content)
                })

        # 2. Get tools in LiteLLM format from universal registry
        litellm_tools = registry.get_litellm_tools() if chat_options.tools else None
        
        # 3. Get tool_choice from chat_options
        tool_choice = None
        if litellm_tools and chat_options.tool_choice:
            if hasattr(chat_options.tool_choice, 'value'):
                tool_choice = chat_options.tool_choice.value
            else:
                tool_choice = str(chat_options.tool_choice)

        # 4. Call LiteLLM with tools - now returns full response data
        response_data = await self.client.chat(
            history=litellm_messages,
            tools=litellm_tools,
            tool_choice=tool_choice
        )

        # 5. Handle error responses
        if isinstance(response_data, str):
            # Error message
            return ChatResponse(
                messages=[ChatMessage(role="assistant", text=response_data)],
                response_id="error"
            )

        # 6. Parse response - check for tool_calls
        choice = response_data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        # 7. Convert to MAF format
        if tool_calls:
            # Response contains tool calls - convert to FunctionCallContent
            maf_contents = []
            
            for tool_call in tool_calls:
                func_data = tool_call.get("function", {})
                func_name = func_data.get("name", "")
                func_args_str = func_data.get("arguments", "{}")
                
                # Parse arguments JSON
                try:
                    func_args = json.loads(func_args_str)
                except:
                    func_args = {}
                
                # Create FunctionCallContent
                maf_contents.append(
                    FunctionCallContent(
                        call_id=tool_call.get("id", ""),
                        name=func_name,
                        arguments=json.dumps(func_args)
                    )
                )
            
            # Return message with tool calls
            return ChatResponse(
                messages=[
                    ChatMessage(role="assistant", contents=maf_contents)
                ],
                response_id=response_data.get("id", "litellm-response")
            )
        else:
            # Regular text response
            return ChatResponse(
                messages=[
                    ChatMessage(role="assistant", text=content)
                ],
                response_id=response_data.get("id", "litellm-response")
            )

    async def _inner_get_streaming_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> AsyncIterable[ChatResponseUpdate]:
        """
        Streaming implementation.
        """
        response = await self._inner_get_response(messages=messages, chat_options=chat_options, **kwargs)
        
        # Get first message
        if response.messages:
            msg = response.messages[0]
            if hasattr(msg, 'contents') and msg.contents:
                # Has contents (tool calls or other)
                yield ChatResponseUpdate(
                    role="assistant",
                    contents=[c.to_dict() for c in msg.contents]
                )
            else:
                # Text message
                yield ChatResponseUpdate(
                    role="assistant", 
                    contents=[{"type": "text", "text": msg.text}]
                )
