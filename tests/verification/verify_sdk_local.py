import asyncio
from src.clients.litellm_client import LiteLLMChatClient
from src.adapters.maf_adapter import LiteLLMModelClient
from agent_framework import ChatMessage

async def main():
    print("--- Verifying SDK Adapter (via LiteLLM) ---")
    
    # 1. Initialize LiteLLM Client (our abstraction layer)
    litellm_client = LiteLLMChatClient(model_name="maf-ollama/llama3.1")
    
    # 2. Initialize SDK Adapter (wraps LiteLLM)
    adapter = LiteLLMModelClient(client=litellm_client)
    
    # 3. Create SDK Request
    messages = [
        ChatMessage(role="user", text="What is the capital of France? Answer in one word.")
    ]
    
    # 4. Call Adapter
    print("Sending request to SDK adapter (via LiteLLM)...")
    response = await adapter.get_response(messages=messages)
    
    # 5. Verify Response
    content = response.messages[0].text
    print(f"Response: {content}")
    
    if "Paris" in content or "paris" in content.lower():
        print("\nSUCCESS: SDK adapter correctly routed request through LiteLLM to Ollama.")
    else:
        print(f"\nPartial Success: Got response from Ollama via LiteLLM.")

if __name__ == "__main__":
    asyncio.run(main())
