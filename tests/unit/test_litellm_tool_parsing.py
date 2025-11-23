import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.clients.litellm_client import LiteLLMChatClient
from agent_framework import ChatResponse

@pytest.mark.asyncio
async def test_litellm_client_ignores_tool_calls():
    """
    Reproduction test: Verifies that the current LiteLLMChatClient 
    fails to return tool calls in the ChatResponse.
    """
    client = LiteLLMChatClient()
    
    # Mock response data simulating an OpenAI tool call response
    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "get_time",
                                "arguments": "{}"
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    # Patch the chat method to return our mock data directly
    # (bypassing the actual HTTP call for this unit test)
    with patch.object(client, 'chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_response_data
        
        # Call get_response
        response = await client.get_response("What time is it?")
        
        # ASSERTION: This should currently FAIL because the client ignores tool_calls
        # The current implementation returns ChatResponse(text="") when content is None
        
        print(f"Response text: '{response.text}'")
        
        # We expect the client to return a ChatResponse where the message contains FunctionCallContent
        assert len(response.messages) > 0, "Should have at least one message"
        message = response.messages[-1]
        
        # Check if any content is a FunctionCallContent
        from agent_framework import FunctionCallContent
        function_calls = [c for c in message.contents if isinstance(c, FunctionCallContent)]
        
        print(f"Function calls found: {len(function_calls)}")
        
        assert len(function_calls) == 1, "Should have 1 function call content"
        assert function_calls[0].name == "get_time", "Tool name should be get_time"
        assert function_calls[0].call_id == "call_123", "Tool call ID should match"
