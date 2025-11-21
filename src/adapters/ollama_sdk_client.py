from typing import Any, MutableSequence, AsyncIterable
from agent_framework import BaseChatClient, ChatResponse, ChatMessage, ChatOptions, ChatResponseUpdate
import httpx

class OllamaSDKClient(BaseChatClient):
    """
    A direct Ollama client that implements the Microsoft Agent Framework's 
    BaseChatClient interface. Calls Ollama's OpenAI-compatible API directly.
    """
    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.base_url = base_url

    async def _inner_get_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Calls Ollama's OpenAI-compatible chat API.
        """
        # 1. Convert SDK messages to Ollama format
        ollama_messages = []
        for msg in messages:
            role = str(msg.role.value) if hasattr(msg.role, 'value') else str(msg.role)
            content = msg.text if hasattr(msg, 'text') else str(msg.content)
            ollama_messages.append({
                "role": role,
                "content": content
            })

        # 2. Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": ollama_messages,
            "stream": False
        }

        # 3. Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

        # 4. Extract response text
        response_text = data["choices"][0]["message"]["content"]

        # 5. Convert to SDK format
        return ChatResponse(
            messages=[
                ChatMessage(role="assistant", text=response_text)
            ],
            response_id=data.get("id", "ollama-response")
        )

    async def _inner_get_streaming_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> AsyncIterable[ChatResponseUpdate]:
        """
        Streaming implementation (non-streaming for now).
        """
        response = await self._inner_get_response(messages=messages, chat_options=chat_options, **kwargs)
        yield ChatResponseUpdate(
            role="assistant", 
            contents=[{"type": "text", "text": response.messages[0].text}]
        )
